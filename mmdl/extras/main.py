# ###################################
# INTIAL MVP
# ###################################
from __future__ import unicode_literals
from lxml.cssselect import CSSSelector
from lxml.html import fromstring

import threading
import asyncio
import time

from pathlib import Path
import os, sys
import warnings
from functools import cache

from youtubesearchpython.__future__ import VideosSearch
import youtube_dl
from ytmusicapi import YTMusic
import eyed3
import urllib
YTMusic = YTMusic()

import logging
import questionary
from rich import print, pretty
from rich.traceback import install
install()
pretty.install()
from rich.progress import track
from rich.console import Console
from rich.prompt import Prompt
console = Console()
from rich.logging import RichHandler
log = logging.getLogger("rich")
DEBUG = False

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

warnings.filterwarnings("ignore")
start_time = time.time()
if not DEBUG:
    blockPrint()
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }
    ],
    'outtmpl': './music/%(title)s.%(ext)s',
    'quiet': True,
    'ignoreerrors': True
}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    try:
        ydl.cache.remove()
    except youtube_dl.DownloadError as error:
        pass
if not DEBUG:
    enablePrint()
console.print("""

.88b  d88. db    db .d8888. d888888b  .o88b.        d8888b. db      
88'YbdP`88 88    88 88'  YP   `88'   d8P  Y8        88  `8D 88      
88  88  88 88    88 `8bo.      88    8P             88   88 88      
88  88  88 88    88   `Y8b.    88    8b      C8888D 88   88 88      
88  88  88 88b  d88 db   8D   .88.   Y8b  d8        88  .8D 88booo. 
YP  YP  YP ~Y8888P' `8888Y' Y888888P  `Y88P'        Y8888D' Y88888P [red]by [link=https://github.com/techboy-coder]@techboy-coder[/link]
                                                                    Find me on github: https://github.com/techboy-coder
[/red]
""", style="blue bold", highlight=False)

async def find_song_from_yt(title: str):
    return VideosSearch(title, limit = 2).next()

def downloader(url: str):
    class MyLogger(object):
        def debug(self, msg):
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            # print(msg)
            pass
    def my_hook(d):
        if d['status'] == 'finished':
            console.print("[blue][=][/blue] [cyan italic]Done downloading. Now converting to mp3. [/cyan italic] Song: "+url["result"][0]["title"])
    console.print("[green][>][/green] Starting to download: "+url["result"][0]["title"])
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }
        ],
        'outtmpl': './music/%(title)s.%(ext)s',
        'quiet': True,
        'ignoreerrors': True,
        "logger":MyLogger(),
        'progress_hooks': [my_hook],
        'restrictfilenames':True,
        'forcefilename':True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url["result"][0]["link"], download=False)
            filename = ydl.prepare_filename(info)
            path = os.getcwd()
            filename = filename.replace("webm","mp3")
            filename = filename.replace("m4a","mp3")
            filepath = Path(path+"/"+filename)
            exists=filepath.is_file()
            if not exists:
                info = ydl.extract_info(url["result"][0]["link"], download=True)
                filename = ydl.prepare_filename(info)
                path = os.getcwd()
                filename = filename.replace("webm","mp3")
                filename = filename.replace("m4a","mp3")
                filepath = Path(path+"/"+filename)
                exists=filepath.is_file()
            else:
                console.print("[cyan][>][/cyan] Song already exists: "+url["result"][0]["title"])
            # console.log(url["result"][0]["id"])
            try:
                meta=YTMusic.get_song(url["result"][0]["id"])
                audiofile = eyed3.load(filename)
                audiofile.tag.artist = meta["videoDetails"]["author"]
                audiofile.tag.title = meta["videoDetails"]["title"]
                response = urllib.request.urlopen(url["result"][0]["thumbnails"][0]["url"])  
                imagedata = response.read()
                audiofile.tag.images.set(3, imagedata , "image/jpeg" ,"Description")
                audiofile.tag.save()
                console.print("[cyan][+][/cyan] [bold]Added metadata for: [/bold]"+url["result"][0]["title"])
            except Exception as e:
                console.print("[red][-][/red] [bold]Could not add metadata for: [/bold]"+url["result"][0]["title"])
                if DEBUG:
                    log.exception(e)
            # console.log(meta)
            if exists:
                console.print("[green][+][/green] [green]Done with: [/green]"+url["result"][0]["title"])
            if not exists:
                console.print("[red][-][/red] [red]Could not download: [/red]"+url["result"][0]["title"])
            return filepath
        except Exception as e:
            if DEBUG:
                log.exception(e)

    

async def run(songs_list):
    console.print("[bold blue][*][/bold blue] Starting to search YT for songs...")
    search_results = [asyncio.create_task(find_song_from_yt(i)) for i in songs_list]
    search_results = await asyncio.gather(*search_results)

    results=[]
    for task in track(
        asyncio.as_completed(search_results),
        description="Searching Youtube...",
        total=len(search_results),
    ):
        results.append(await task)

    
    for i in range(len(results)):
        results[i]["title"]=songs_list[i] # Does this really work?

    console.print("[bold blue][*][/bold blue] Finished searching songs. Downloading %s songs..." % len(results))
    threads = []
    for song in results:
        # url = song
        thread = threading.Thread(target=downloader, args=(song,))
        threads.append(thread)
    
    # Actually start downloading
    for thread in threads:
        thread.start()
     
    # Wait for all the downloads to complete
    with console.status("[bold]Downloading Songs, please wait (this can take some time)...[/bold]", spinner="bouncingBar") as status:
        for thread in threads: 
            thread.join()
    console.print("[bold blue][*][/bold blue] Finished downloading Songs. Downloaded a total of %s songs." % len(results))

def main(songs_list):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(songs_list))
    loop.close()

single_songs = questionary.select(
    "How many songs do you want to download?",
    choices=[
        "One song",
        "Multiple Songs"
    ]
).ask()

if single_songs == "One song":
    main([questionary.text("What is the song name").ask()])
else:
    input_method = questionary.select(
        "Which songs do you want to download?",
        choices=[
            "Songs, comma seperated",
            'List in textfile (1 Song per line)',
            'From YTMusic (beta)',
        ]).ask()  # returns value of selection

    if input_method == "From YTMusic":
        console.print("""[bold red]YT-Music[/bold red]. 
        - Go to your YTMusic liked songs playlist (https://music.youtube.com/playlist?list=LM)
        - Make sure you are logged in
        - Press Ctrl/Cmd + Shift + i and open the dev tools
        - Keep scrolling down until you reach the end of your playlist (Songs will stop loading)
        - Copy the all the html markup
        - Create a text file and paste the html into it.
        """)
        if not questionary.confirm("Only continue if you have done the task.").ask():
            quit()
        file = questionary.path("Where is that filelocated?").ask()
        with open(file, "r", encoding="utf-8") as f:
            data = f.read()
        h = fromstring(data)
        sel = CSSSelector("yt-formatted-string.title.style-scope.ytmusic-responsive-list-item-renderer.complex-string > a.yt-simple-endpoint.style-scope.yt-formatted-string")
        song_list=[e.text for e in sel(h)]
        main(song_list)

    elif input_method=="List in textfile (1 Song per line)":
        file = questionary.path("Where is that file located?").ask()
        text_file = open(file ,encoding='utf-8')
        songs_list = text_file.read().splitlines()
        main(songs_list)
    elif input_method=="Songs, comma seperated":
        songs_list = questionary.text("Write all songs (comma seperated)").ask().split(",")
        main(songs_list)
path = os.getcwd()
console.print("[>] Music has been downloaded to:", Path(path).joinpath("./music"), style="blue bold")
console.print("[>] Total time needed: %.2f seconds." % (time.time() - start_time), style="blue bold")