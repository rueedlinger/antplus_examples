import asyncio
import json
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

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
        app.state.metrics.stop()


app = FastAPI(title="ANT+ Service", lifespan=lifespan)


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
    try:
        app.state.metrics.start()
        return {"message": "Metrics collection started"}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start metrics: {str(e)}"
        )


@app.post("/metrics/stop")
def stop_metrics():
    try:
        app.state.metrics.stop()
        return {"message": "Metrics collection stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop metrics: {str(e)}")


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
