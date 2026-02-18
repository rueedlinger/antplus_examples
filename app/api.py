import asyncio
import time
import json
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.ant import Metrics
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- startup ----
    app.state.metrics = Metrics()
    yield
    # ---- shutdown ----
    if app.state.metrics:
        # app.state.metrics.stop()
        pass


app = FastAPI(title="ANT+ Metrics Service", lifespan=lifespan)
templates = Jinja2Templates(directory="templates")


class WheelCircumferenceUpdate(BaseModel):
    wheel_circumference_m: float = Field(
        ..., gt=0, description="Wheel circumference in meters"
    )


class SensorModel(BaseModel):
    device_id: int
    device_type: int
    name: str


class MetricsResponse(BaseModel):
    power: Optional[float]
    speed: Optional[float]
    cadence: Optional[float]
    distance: Optional[float]
    heart_rate: Optional[int]
    wheel_circumference_m: float
    is_running: bool


# -------------------------
# Metrics endpoints
# -------------------------


@app.post("/metrics/start")
def start_metrics():
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            app.state.metrics.start()
            return {"message": "Metrics collection started"}
        except Exception as e:
            logging.warning(f"Failed to start metrics (attempt {attempt}): {str(e)}")
            time.sleep(0.5)  # brief pause before retrying

    # If all retries failed, raise HTTPException
    raise HTTPException(
        status_code=500, detail=f"Failed to start metrics after {max_retries} attempts"
    )


@app.post("/metrics/stop")
def stop_metrics():
    try:
        app.state.metrics.stop()
        return {"message": "Metrics collection stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop metrics: {str(e)}")


@app.post("/metrics/wheel_circumference")
def update_wheel_circumference(payload: WheelCircumferenceUpdate):
    try:
        app.state.metrics.set_wheel_circumference(payload.wheel_circumference_m)
        return {
            "message": f"Wheel circumference updated to {payload.wheel_circumference_m} m"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update: {str(e)}")


@app.get("/metrics", response_model=MetricsResponse)
def get_metrics():
    try:
        metrics = app.state.metrics.get_metrics()
        return MetricsResponse(**metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@app.get("/metrics/devices", response_model=list[SensorModel])
def get_metrics_devices():
    try:
        devices = app.state.metrics.get_devices()
        return [SensorModel(**d) for d in devices]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get devices: {str(e)}")


async def metrics_event_generator():
    while True:
        try:
            # Get current metrics from your app state
            metrics = app.state.metrics.get_metrics()

            # Convert to JSON string
            data = json.dumps(metrics)

            # SSE format: `data: <payload>\n\n`
            yield f"data: {data}\n\n"

            # Send updates every second (adjust as needed)
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            # Client disconnected
            break
        except Exception as e:
            # Send error to client
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            await asyncio.sleep(1)


@app.get("/metrics/stream")
async def stream_metrics():
    return StreamingResponse(metrics_event_generator(), media_type="text/event-stream")


async def device_event_generator():
    last_devices = []
    while True:
        try:
            # Get current devices from app state
            devices = app.state.metrics.get_devices()  # returns list of dicts
            # Only yield if changed
            if devices != last_devices:
                last_devices = devices
                yield f"data: {json.dumps(devices)}\n\n"
            await asyncio.sleep(1)  # adjust frequency as needed
        except asyncio.CancelledError:
            # client disconnected
            break
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            await asyncio.sleep(1)


@app.get("/metrics/devices/stream")
async def stream_devices():
    return StreamingResponse(device_event_generator(), media_type="text/event-stream")


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})
