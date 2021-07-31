import logging, asyncio, sys, os
from pathlib import Path
from rich.logging import RichHandler
import concurrent.futures

# log=logging

class Utils:
  @staticmethod
  def log_handler(debug, msg, level: str):
    """Logging. All logging happens from here.

    Args:
        debug (bool): Should you log anything, or surpress warnings to
        msg (str/error): Message
        level (str): Choose type: (debug, info, warning, error, critical)
    """    
    if debug:
        FORMAT = "%(message)s"
        logging.basicConfig(
            level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
        )
        log = logging.getLogger("rich")
        if level.lower() == "debug":
            log.debug(msg)
        elif level.lower() == "info":
            log.info(msg)
        elif level.lower() == "warning":
            log.warning(msg)
        elif level.lower() == "error":
            log.error(msg)
        elif level.lower() == "critical":
            log.critical(msg)

  @staticmethod
  def run_async(function, *args):
    loop = asyncio.get_event_loop()
    out=loop.run_until_complete(function(*args))
    loop.close()
    return out
    
  # Disable
  @staticmethod
  def blockPrint():
    sys.stdout = open(os.devnull, 'w')

  # Restore
  @staticmethod
  def enablePrint():
    sys.stdout = sys.__stdout__
    
  @staticmethod
  def get_cwd():
    return os.getcwd()

  @staticmethod
  def check_file_exists(filepath: str, rest):
    # print("lkj")
    # print(path, filepath)
    # print(Path(path+"/"+filepath).is_file())
    return [Path(filepath).is_file(), rest]