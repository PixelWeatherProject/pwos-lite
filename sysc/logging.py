LEVEL_INFO = 0
LEVEL_WARN = 1
LEVEL_ERROR = 2
LEVEL_DEBUG = 3

COLOR_INFO = "\x1b[1;94m"
COLOR_WARN = "\x1b[1;33m"
COLOR_ERROR = "\x1b[1;91m"
COLOR_DEBUG = "\x1b[1;95m"
RESET_COLOR = "\x1b[0m"

def os_info(module, msg) -> None:
    _log(LEVEL_INFO, module, msg)

def os_warn(module, msg) -> None:
    _log(LEVEL_WARN, module, msg)

def os_error(module, msg) -> None:
    _log(LEVEL_ERROR, module, msg)

def os_debug(module, msg) -> None:
    _log(LEVEL_DEBUG, module, msg)

def _log(lvl, module, msg) -> None:
    _print_lvl(lvl)
    print(" [", module, "] ", sep="", end="")
    print(msg)

def _print_lvl(lvl: str) -> None:
    if lvl == LEVEL_INFO:
        print(COLOR_INFO, "INFO", RESET_COLOR, sep="", end="")
    elif lvl == LEVEL_WARN:
        print(COLOR_WARN, "WARN", RESET_COLOR, sep="", end="")
    elif lvl == LEVEL_ERROR:
        print(COLOR_ERROR, "ERROR", RESET_COLOR, sep="", end="")
    elif lvl == LEVEL_DEBUG:
        print(COLOR_DEBUG, "DEBUG", RESET_COLOR, sep="", end="")
    else:
        raise ValueError("Invalid log level")