import colorama

# init the colorama module (for terminal coloured pretty output)
colorama.init()

YELLOW = colorama.Fore.YELLOW
RED = colorama.Fore.LIGHTRED_EX
GREEN = colorama.Fore.GREEN
BLUE = colorama.Fore.BLUE

RESET = colorama.Fore.RESET


class Logger:
    """
    Simple Logger class
    contains predefined methods for pretty log.
    """

    @staticmethod
    def log_sys(msg):
        print(f"{BLUE}[SYS] {msg}{RESET}") if LOG_EVENTS else ''

    @staticmethod
    def log_info(msg):
        print(f"{GREEN}[APP] {msg}{RESET}") if LOG_EVENTS else ''

    @staticmethod
    def log_warning(msg):
        print(f"{YELLOW}[INFO] {msg}{RESET}") if LOG_EVENTS else ''

    @staticmethod
    def log_error(msg):
        print(f"{RED}[ERR] {msg}{RESET}") if LOG_EVENTS else ''


# log program events
LOG_EVENTS = False
