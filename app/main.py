from time import sleep
from app.ant import Monitor


def main():
    m = Monitor()
    m.start()
    try:
        while True:
            m.display()
            sleep(0.1)
    except KeyboardInterrupt:
        m.stop()


if __name__ == "__main__":
    main()
