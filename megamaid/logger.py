# Stdlib imports
import logging
import threading

# Internal imports
from megamaid.edict import *
from megamaid.utils import *


class CustomFormatter(logging.Formatter):

    COLORS = Edict(
        **{
            # Formatting
            "bold": "\033[1m",
            "underline": "\033[4m",
            "blink": "\033[5m",
            "end": "\033[0m",
            # Foreground colors
            "black": "\033[30m",
            "red": "\033[31m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "blue": "\033[34m",
            "purple": "\033[35m",
            "cyan": "\033[36m",
            "white": "\033[37m",
            # Background colors
            "bg_black": "\033[40m",
            "bg_red": "\033[41m",
            "bg_green": "\033[42m",
            "bg_yellow": "\033[43m",
            "bg_blue": "\033[44m",
            "bg_purple": "\033[45m",
            "bg_cyan": "\033[46m",
            "bg_white": "\033[47m",
        }
    )

    _c_debug = f"{COLORS.bold}{COLORS.purple}"
    _c_info = f"{COLORS.bold}{COLORS.green}"
    _c_warning = f"{COLORS.bold}{COLORS.yellow}"
    _c_error = f"{COLORS.bold}{COLORS.red}"

    _m_asctime = (
        f"{COLORS.bold}{COLORS.underline}{COLORS.cyan}%(asctime)-15s{COLORS.end}"
    )
    _m_level = f"{COLORS.bold}{COLORS.underline}%(levelname)-8s{COLORS.end}"
    _m_name = f"{COLORS.bold}{COLORS.purple}%(name)-10s{COLORS.end}"
    _m_message = "%(message)s"

    FORMATS = {
        logging.DEBUG: f"{_c_debug}{_m_level} {_m_message}",
        logging.INFO: f"{_c_info}{_m_level} {_m_message}",
        logging.WARNING: f"{_c_warning}{_m_level} {_m_message}",
        logging.ERROR: f"{_c_error}{_m_level} {_m_message}",
        logging.CRITICAL: f"{_c_error}{_m_level} {_m_message}",
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class Logger(threading.Thread):
    def __init__(self, log_q, tui=False, gui=False):
        threading.Thread.__init__(self)
        self.log_q = log_q
        self.logger = logging.getLogger("MegaMaid")
        self.logger.setLevel(logging.INFO)
        if not tui and not gui:
            self.stream = logging.StreamHandler()
            self.stream.setLevel(logging.INFO)
            self.stream.setFormatter(CustomFormatter())
        self.logger.addHandler(self.stream)

    def run(self):
        while True:
            log = self.log_q.get()
            if log == "EXIT":
                break
            if type(log) is str:
                self.logger.info(f"{log}")
            elif type(log) is dict and log.get("level", False):
                eval(
                    f"self.logger.{log.get('level', 'info')}('{log.get('message', '')}')"
                )

        self.logger.info("Logger thread exiting")
        return
