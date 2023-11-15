import logging
import os
import sys
import time


class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ""

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass


def get_logger(logfile=None, remove_if_any=False, timestamp=False):
    """
    Return a logger that log on stdout and in LOGFILE
    logfile default filename is 'run.log'
    if timestamp is True timestamp is added to the filename
    if remove_if_any is set to True, old run.log is removed
    """
    timestr = time.strftime("%Y-%m-%d_%Hh%Mmin%Ssec", time.localtime())
    if timestamp:
        if not logfile:
            logfile = "run_{}.log".format(timestr)
        else:
            logfile = logfile.split(".log", 1)[0]
            logfile = "{}_{}.log".format(logfile, timestr)
    else:
        if not logfile:
            logfile = "run.log"
        if remove_if_any:
            if os.path.isfile("{}".format(logfile)):
                os.remove("{}".format(logfile))
        if not logfile.endswith(".log"):
            logfile = "{}.log".format(logfile)

    logging.basicConfig(filename=logfile, level=logging.INFO, filemode="a")
    logger = logging.getLogger("")

    if len(logger.handlers) == 1:
        logging.getLogger("").addHandler(logging.StreamHandler())

    stdout_logger = logging.getLogger("STDOUT")
    sl = StreamToLogger(stdout_logger, logging.INFO)
    sys.stdout = sl

    stderr_logger = logging.getLogger("STDERR")
    sl = StreamToLogger(stderr_logger, logging.ERROR)
    sys.stderr = sl

    return logger.info
