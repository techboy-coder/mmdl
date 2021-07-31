##############################################################
# Published on ... under the MIT Licence
# Copyright 2021 techboy-coder
#               _ _ 
#               | | |
# _ __ ___   __| | |
# | '_ ` _ \ / _` | |
# | | | | | | (_| | |   by @techboy-coder
# |_| |_| |_|\__,_|_|   find me on https://github.com/techboy-coder
                                                    
# MDL [Music Downloader] - A tool to easily download music.
##############################################################
from __future__ import unicode_literals
from lxml.cssselect import CSSSelector
from lxml.html import fromstring
import click
from mdl import MusicDownloader
from ask import asker
from rich.console import Console
import questionary
console = Console()
from click_help_colors import HelpColorsGroup, HelpColorsCommand
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS, cls=HelpColorsGroup, help_headers_color='red', help_options_color='green')
def main():
  """\b                                             
                _ _ 
                | | |
  _ __ ___   __| | |
  | '_ ` _ \ / _` | |
  | | | | | | (_| | |   by @techboy-coder
  |_| |_| |_|\__,_|_|   find me on https://github.com/techboy-coder
                                                      
  MDL [Music Downloader] - A tool to easily download music.

  > Enter 'mdl go' to start downloading songs.
  """
  pass

@main.command(context_settings=CONTEXT_SETTINGS, cls=HelpColorsCommand, help_headers_color='red', help_options_color='green')
@click.option("-v","--verbose", help="Verbose level", type=int, required=False, default=1)
@click.option("-d","--debug", help="Enable debug mode", is_flag=True)
def go(verbose, debug):
  """
  Easy mode. Just answer few questions and download your songs.

  MDL [Music Downloader] - A tool to easily download music. \n
  
  # Go Command
  > Easy way to download songs. Uses inputs/inquirer. (Simply run 'mdl go')
  """

  if debug:
    console.log("Verbose: ", verbose)
    console.log("Debug: ", debug)

  console.print("""\b[red]
                _ _ 
                | | |
  _ __ ___   __| | |
  | '_ ` _ \ / _` | |
  | | | | | | (_| | |   [/red]by @techboy-coder[red]
  |_| |_| |_|\__,_|_|   [/red]find me on https://github.com/techboy-coder
                                                      
  [green]MDL [Music Downloader] - A tool to easily download music.[/green]
  """)
  song_names=asker()
  console.print("\n[cyan]> [/] Total number of songs: %s. \n" % (len(song_names)))
  # List, verbose, debug
  MusicDownloader(song_names, verbose, debug).download_songs()

@main.group(context_settings=CONTEXT_SETTINGS, cls=HelpColorsGroup, help_headers_color='red', help_options_color='green')
def download():
  """
  Download your songs the way you want!

  MDL [Music Downloader] - A tool to easily download music. \n
  # Download Section
  > Here are possible ways to download songs.
  Ways to download:\n
  - Single song\n
  - Multiple songs\n
    - From file\n
    - As multiple songs (e.g. song1, song2, song3, ...)\n
    - From your YTMusic liked songs playlist (beta)\n
  """
  pass

@download.command(context_settings=CONTEXT_SETTINGS, cls=HelpColorsCommand, help_headers_color='red', help_options_color='green')
@click.argument("file", type=click.File("r"), required=True)
@click.option("-s","--seperator", help="Seperator of song_names", type=str, default="\n")
@click.option("-v","--verbose", help="Verbose level", type=int, required=False, default=1)
@click.option("-d","--debug", help="Enable debug mode", is_flag=True)
def file(file, seperator, verbose, debug):
  """
  Get songs from a file and then download them.

  MDL [Music Downloader] - A tool to easily download music.

  ## File Section
  > Download multiple songs from a file.
  
  Run 'mdl download file <filepath e.g. ~/Downloads/file.txt>'.
  """

  # print(type(file))
  # text_file = open(file ,encoding='utf-8')
  songs = file.read().split(seperator)
  if debug:
    console.log("File: ", file)
    console.log("Seperator: ", repr(seperator))
    console.log("Songs: ", str(songs))
    console.log("Verbose: ", verbose)
    console.log("Debug: ", debug)

  console.print("""\b[red]
                _ _ 
                | | |
  _ __ ___   __| | |
  | '_ ` _ \ / _` | |
  | | | | | | (_| | |   [/red]by @techboy-coder[red]
  |_| |_| |_|\__,_|_|   [/red]find me on https://github.com/techboy-coder
                                                      
  [green]MDL [Music Downloader] - A tool to easily download music.[/green]
  """)
  console.print("\n[cyan]> [/] Total number of songs: %s. \n" % (len(songs)))
  if not questionary.confirm("Do you want to continue").ask():
    quit()
  # file, verbose, debug
  MusicDownloader(songs, verbose, debug).download_songs()
  return
  
@download.command(context_settings=CONTEXT_SETTINGS, cls=HelpColorsCommand, help_headers_color='red', help_options_color='green')
@click.argument("songs", type=str, nargs=-1, required=False)
# @click.argument("seperator", type=str, required=True, nargs=1, default=",")
@click.option("-v","--verbose", help="Verbose level", type=int, required=False, default=1)
@click.option("-d","--debug", help="Enable debug mode", is_flag=True)
@click.option("-a","--ask", help="Get songs via input (easy)", is_flag=True)
def list(songs, verbose, debug, ask):
  """
  Download multiple songs.

  MDL [Music Downloader] - A tool to easily download music.

  ## List Section/Multiple Songs
  > Download multiple songs from a list.
  
  Run 'mdl download list "Term1" "Term2" --ask (or -a)'.
  > Write all songs search terms (comma seperated): Term3, Term 4
  > This will download Term1, Term2, Term3, Term4

  """
  if ask:
    console.print("[cyan][>][/] We'll be manually asking you for songs.")
    songs_list = questionary.text("Write all songs search terms (comma seperated)").ask()
    if not songs_list:
      quit()
    songs_list = songs_list.split(",")
  else:
    if len(songs) < 1:
      console.print("[cyan][-][/] You didn't specify any songs. So we'll be manually asking them to you.")
      songs_list = questionary.text("Write all songs search terms (comma seperated)").ask()
      if not songs_list:
        quit()
      songs_list = songs_list.split(",")
    else:
      songs_list = []
    if isinstance(songs, tuple):
      s = [song for song in songs]+songs_list
      songs_list = s
  if debug:
    console.log("Songs: ", songs_list)
    console.log("Verbose: ", verbose)
    console.log("Debug: ", debug)

  console.print("""\b[red]
                _ _ 
                | | |
  _ __ ___   __| | |
  | '_ ` _ \ / _` | |
  | | | | | | (_| | |   [/red]by @techboy-coder[red]
  |_| |_| |_|\__,_|_|   [/red]find me on https://github.com/techboy-coder
                                                      
  [green]MDL [Music Downloader] - A tool to easily download music.[/green]
  """)
  console.print("\n[cyan]> [/] Total number of songs: %s. \n" % (len(songs_list)))
  # file, verbose, debug
  MusicDownloader(songs_list, verbose, debug).download_songs()
  return
  
@download.command(context_settings=CONTEXT_SETTINGS, cls=HelpColorsCommand, help_headers_color='red', help_options_color='green')
@click.argument("file", type=click.File("r"), required=False)
# @click.argument("seperator", type=str, required=True, nargs=1, default=",")
@click.option("-v","--verbose", help="Verbose level", type=int, required=False, default=1)
@click.option("-d","--debug", help="Enable debug mode", is_flag=True)
@click.option("-a","--ask", help="Get songs via input (easy)", is_flag=True)
def ytmusic(file, verbose, debug, ask):
  if not ask and not file:
    ask = True
  """
  Download multiple songs from YouTube Music Liked songs.

  MDL [Music Downloader] - A tool to easily download music.

  ## YTMusic Section
  > Download multiple songs from YTMusic liked songs (beta). [Done via parsing html.]
  
  Run 'mdl download ytmusic <filepath e.g. ~/Downloads/file.txt> (or --ask or -a for entering file via input)'.

  """
  if ask:
    console.print("[cyan][>][/] We'll be manually asking you for the file location.")
    console.print("""
[bold red]YT-Music[/bold red]. 
- Go to your YTMusic liked songs playlist (https://music.youtube.com/playlist?list=LM)
- Make sure you are logged in
- Press Ctrl/Cmd + Shift + i and open the dev tools
- Keep scrolling down until you reach the end of your playlist (Songs will stop loading)
- Copy the all the html markup
- Create a text file and paste the html into it.
                """)
    if not questionary.confirm("Only continue if you have done the task.").ask():
        quit()
    file = questionary.path("Where is that file located?").ask()
    with open(file, "r", encoding="utf-8") as f:
        data = f.read()
    h = fromstring(data)
    sel = CSSSelector("yt-formatted-string.title.style-scope.ytmusic-responsive-list-item-renderer.complex-string > a.yt-simple-endpoint.style-scope.yt-formatted-string")
    songs_list=[e.text for e in sel(h)]
    if not songs_list[0]:
      console.log("[red][-] Hmm. No songs could be parsed from html. Did you select the correct HTML? If you see a error please make a bug report. Thanks!")
      quit()
  if not ask:
    if not file:
      console.log("[red][-] You need to enter the file location or add the -a flag.")
      quit()
    data = file.read()
    h = fromstring(data)
    sel = CSSSelector("yt-formatted-string.title.style-scope.ytmusic-responsive-list-item-renderer.complex-string > a.yt-simple-endpoint.style-scope.yt-formatted-string")
    songs_list=[e.text for e in sel(h)]
    if not songs_list[0]:
      console.log("[red][-] Hmm. No songs could be parsed from html. Did you select the correct HTML? If you see a error please make a bug report. Thanks!")
      console.print("""
[bold red]YT-Music[/bold red]. 
- Go to your YTMusic liked songs playlist (https://music.youtube.com/playlist?list=LM)
- Make sure you are logged in
- Press Ctrl/Cmd + Shift + i and open the dev tools
- Keep scrolling down until you reach the end of your playlist (Songs will stop loading)
- Copy the all the html markup
- Create a text file and paste the html into it.
      """)

  
  if debug:
    console.log("Songs: ", str(songs_list))
    console.log("Verbose: ", verbose)
    console.log("Debug: ", debug)
  console.print("""\b[red]
                _ _ 
                | | |
  _ __ ___   __| | |
  | '_ ` _ \ / _` | |
  | | | | | | (_| | |   [/red]by @techboy-coder[red]
  |_| |_| |_|\__,_|_|   [/red]find me on https://github.com/techboy-coder
                                                      
  [green]MDL [Music Downloader] - A tool to easily download music.[/green]
  """)
  console.print("\n[cyan]> [/] Total number of songs: %s. \n" % (len(songs_list)))
  if not questionary.confirm("Do you want to continue").ask():
    quit()
  # file, verbose, debug
  MusicDownloader(songs_list, verbose, debug).download_songs()
  return
  

@download.command(context_settings=CONTEXT_SETTINGS, cls=HelpColorsCommand, help_headers_color='red', help_options_color='green')
@click.argument("song", type=str, required=True, nargs=-1)
@click.option("-v","--verbose", help="Verbose level", type=int, required=False, default=1)
@click.option("-d","--debug", help="Enable debug mode", is_flag=True)
def single(song, verbose, debug):
  """
  Download a single song based on search query.

  MDL [Music Downloader] - A tool to easily download music.

  ## Single Song Section
  > Download a single song based on search query.
  
  Run 'mdl download single <songname>'.
  """

  # print(type(file))
  song = " ".join(song)

  # text_file = open(file ,encoding='utf-8')
  if debug:
    console.log("File: ", song)
    console.log("Songs: ", str(songs))
    console.log("Verbose: ", verbose)
    console.log("Debug: ", debug)

  console.print("""\b[red]
                _ _ 
                | | |
  _ __ ___   __| | |
  | '_ ` _ \ / _` | |
  | | | | | | (_| | |   [/red]by @techboy-coder[red]
  |_| |_| |_|\__,_|_|   [/red]find me on https://github.com/techboy-coder
                                                      
  [green]MDL [Music Downloader] - A tool to easily download music.[/green]
  """)
  songs = [song]
  console.print("\n[cyan]> [/] Song: %s. \n" % (song))
  # file, verbose, debug
  MusicDownloader(songs, verbose, debug).download_songs()
  return
  


if __name__ == '__main__':
  main()
  # :/ 