import logging
import time
import inspect

logging.basicConfig(
    filename="./data/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

THRESHOLD = 1


def time_def(func, args=[]):
    start = time.time()
    res = func(*args)
    end = time.time() - start
    stack = inspect.stack()
    msg = f"{stack} took {end} seconds to execute"
    if end > THRESHOLD:
        logger.warning(msg)
    else:
        logger.info(msg)
    return res


def log_error(msg):
    print("Unexpected error")
    stack = inspect.stack()
    logger.error(f"{stack} unexpected error: {msg}")


def called_with(args):
    stack = inspect.stack()
    logger.info(f"{stack} called with: {args}")


def log_user_input(input):
    logger.info(f"user entered {input}")
