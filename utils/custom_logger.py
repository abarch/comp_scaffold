import logging
from pathlib import Path

log_folder = Path.cwd().parent / Path("output/temp/logs")
try:
    log_folder.mkdir(parents=True, exist_ok=False)
except FileExistsError:
    print("Folder is already there")
else:
    print("Folder was created")


def getLoggerForFile(name, debug_in_console=False, info_in_console=False):
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    codeLogger = logging.getLogger(name)
    codeLogger.setLevel(logging.DEBUG)

    ch_level = logging.WARNING
    if info_in_console:
        ch_level = logging.INFO
    if debug_in_console:
        ch_level = logging.DEBUG

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(ch_level)

    codeLogger.addHandler(ch)

    log_file = log_folder / f"{name}.log"
    print("log", log_file)

    fh = logging.FileHandler(filename=log_file)
    fh.setFormatter(formatter)
    fh.setLevel(logging.DEBUG)
    codeLogger.addHandler(fh)

    return codeLogger


if __name__ == "__main__":
    print(getLoggerForFile(__name__))
