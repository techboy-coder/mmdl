import logging, asyncio, sys, os
from pathlib import Path
from rich.logging import RichHandler
import concurrent.futures
from rich.console import Console
import questionary
console = Console()

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
    # if any(File.endswith(".mp3") or File.endswith(".mp3") for File in os.listdir(".")):
    #   return True
    # return False
    exists=Path(os.path.splitext(filepath)[0]+".mp3").is_file() or Path(os.path.splitext(filepath)[0]+".m4a").is_file() or Path(os.path.splitext(filepath)[0]+".opus").is_file()
    return [exists, rest]


def print_logo():
  console.print("""\b[red]
                            _ _ 
                          | | |
  _ __ ___  _ __ ___   __| | |
  | '_ ` _ \| '_ ` _ \ / _` | |
  | | | | | | | | | | | (_| | |   [/]by techboy-coder[red]
  |_| |_| |_|_| |_| |_|\__,_|_|   [/]find me on https://github.com/techboy-coder
                                                      
  [green]mmdl [Mega Music Downloader] - A tool to easily download music.[/green]
  """)

def num_of_songs_printer(num):
  console.print("\n[cyan]> [/] Total number of songs: %s. \n" % (num))

def wanna_continue(msg="Do you want to continue? "):
    if not questionary.confirm(msg).ask():
      quit()

def check_file(filename):
    possible_extensions = ('', '.txt', '.dat')
    for e in possible_extensions:
        if os.path.isfile(filename + e): 
            return filename + e
    else:
        return None