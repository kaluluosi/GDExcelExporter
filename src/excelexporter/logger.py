import logging
import sys

FORMAT = "%(name)s-%(levelname)s:%(message)s"

fh = logging.FileHandler("log.txt", "w")
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter(FORMAT))

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
ch.setFormatter(logging.Formatter(FORMAT))

logging.basicConfig(level=logging.DEBUG, handlers=[fh, ch])


def log_uncaught_exceptions(ex_cls, ex, tb):
    logging.critical("未捕获异常", exc_info=(ex_cls, ex, tb))


sys.excepthook = log_uncaught_exceptions
