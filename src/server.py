import task3
import time
from prometheus_client import start_http_server, Summary


s = Summary("daily_job_seconds", "Time taken to finish to background job")


@s.time()
def main():
    task3.daily_job()


if __name__ == "__main__":
    start_http_server(8000)
    main()

    # A loop to keep the script running
    # So I can see the metrics at premetheous
    while True:
        time.sleep(1)
