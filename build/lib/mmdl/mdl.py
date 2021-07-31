from __future__ import unicode_literals
from lxml.cssselect import CSSSelector
from lxml.html import fromstring

import threading
import asyncio
import time

from pathlib import Path
import os, sys
# sys.path.append(os.getcwd())
import warnings
from functools import cache
import concurrent.futures

from youtubesearchpython.__future__ import VideosSearch
import youtube_dl
from ytmusicapi import YTMusic
import eyed3
import urllib

import logging
import questionary
from rich import print, pretty
from rich.traceback import install
install()
# pretty.install()
from rich.progress import track

from .globals import console

from .utils import Utils
from .yt_utils import YtdlUtils


##Dev Dep
import shutil

class DisplayablePath(object):
    display_filename_prefix_middle = '├──'
    display_filename_prefix_last = '└──'
    display_parent_prefix_middle = '    '
    display_parent_prefix_last = '│   '

    def __init__(self, path, parent_path, is_last):
        self.path = Path(str(path))
        self.parent = parent_path
        self.is_last = is_last
        if self.parent:
            self.depth = self.parent.depth + 1
        else:
            self.depth = 0

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

    @classmethod
    def make_tree(cls, root, parent=None, is_last=False, criteria=None):
        root = Path(str(root))
        criteria = criteria or cls._default_criteria

        displayable_root = cls(root, parent, is_last)
        yield displayable_root

        children = sorted(list(path
                               for path in root.iterdir()
                               if criteria(path)),
                          key=lambda s: str(s).lower())
        count = 1
        for path in children:
            is_last = count == len(children)
            if path.is_dir():
                yield from cls.make_tree(path,
                                         parent=displayable_root,
                                         is_last=is_last,
                                         criteria=criteria)
            else:
                yield cls(path, displayable_root, is_last)
            count += 1

    @classmethod
    def _default_criteria(cls, path):
        return True

    @property
    def displayname(self):
        if self.path.is_dir():
            return self.path.name + '/'
        return self.path.name

    def displayable(self):
        if self.parent is None:
            return self.displayname

        _filename_prefix = (self.display_filename_prefix_last
                            if self.is_last
                            else self.display_filename_prefix_middle)

        parts = ['{!s} {!s}'.format(_filename_prefix,
                                    self.displayname)]

        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(self.display_parent_prefix_middle
                         if parent.is_last
                         else self.display_parent_prefix_last)
            parent = parent.parent

        return ''.join(reversed(parts))

class MusicDownloader():
    def __init__(self, song_names: list[str], verbose: int, debug: bool):
        """Music Downloader Class. This is the main class :/

        Args:
            song_names (list[str]): list of all songs/titles you want to download.py
            verbose (int): Verbose level. 0 to INF. (1 and above=same)
            debug (bool): Enable debugging?
        """        
        
        self.song_names = song_names
        self.debug = debug
        self.verbose = verbose
        # self.output_path = download_dir_location
        self.ytdl = YtdlUtils(self)
    
    def find_multiple_songs_by_query(self):
        """Searches Youtube and finds songs by query. Uses "song_names" as a list of songs. Function itself is sync, but runs "async"-ly inside => speed.
        """        
        async def sub_finder(verbose, queries: list[str]):
            search_results = [asyncio.create_task(self.ytdl.find_song_on_yt(query)) for query in queries]
            search_results = await asyncio.gather(*search_results)
            results=[]
            if verbose >= 1:
                for task in track(
                    asyncio.as_completed(search_results),
                    description="Searching Youtube...",
                    total=len(search_results),
                ):
                    results.append(await task)
            else:
                for task in asyncio.as_completed(search_results):
                    results.append(await task)
            return results
        
        result=Utils.run_async(sub_finder, self.verbose, self.song_names)
        return result

    def download_songs(self):  # sourcery no-metrics
        """Downloads songs.
        """        
        start_time = time.time()
        songs_with_meta = self.find_multiple_songs_by_query()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            temp = []
            if self.verbose >= 1:
                for song in songs_with_meta:
                    song_name = executor.submit(self.ytdl.download, song["result"][0]["link"], False, song)
                    temp.append(song_name)

                filenames = [
                    r.result()
                    for r in track(
                        concurrent.futures.as_completed(temp),
                        description="Getting file name(s)...",
                        total=len(temp),
                    )
                ]
                temp = []
                cwd = Utils.get_cwd()
                for f in filenames:
                    # print(f["filename"])
                    does_exist = executor.submit(Utils.check_file_exists, f["filename"], f)
                    temp.append(does_exist)
                exists = [
                    r.result()
                    for r in track(
                        concurrent.futures.as_completed(temp),
                        description="Checking for already existing file(s)...",
                        total=len(temp),
                    )
                ]
                temp=[]
                for f in exists:
                    if not f[0]:
                        song = executor.submit(self.ytdl.download, f[1]["url"], True, f[1])
                        temp.append(song)

                if len(temp) > 1:
                    for r in track(concurrent.futures.as_completed(temp), description="Downloading song(s) (This can take some time)...", total=len(temp)):
                        pass
                else:
                    with console.status("[bold]Downloading single song, please wait...[/bold]", spinner="bouncingBar") as status:
                        for r in concurrent.futures.as_completed(temp):
                            pass

                temp=[]
                for f in exists:
                    song = executor.submit(self.ytdl.get_song_meta_by_v_id, f[1]["rest"]["result"][0]["id"], f)
                    temp.append(song)

                meta = [
                    r.result()
                    for r in track(
                        concurrent.futures.as_completed(temp),
                        description="Getting metadata for song(s)...",
                        total=len(temp),
                    )
                ]
                temp=[]
                for f in meta:
                    song = executor.submit(self.ytdl.change_metadata_of_song, f["rest"][1]["filename"],f["meta"]["videoDetails"]["author"],f["meta"]["videoDetails"]["title"],f["rest"][1]["rest"]["result"][0]["thumbnails"][0]["url"])
                    temp.append(song)
                meta = [
                    r.result()
                    for r in track(
                        concurrent.futures.as_completed(temp),
                        description="Writing metadata to song(s)...",
                        total=len(temp),
                    )
                ]
                if self.verbose > 1:
                    console.print("[cyan bold] \n\n\nAll songs ==> [/]")
                    for i in exists:
                        console.print("   • %s" % (i[1]["rest"]["result"][0]["title"]))
            else:
                console.log("[green][>][/green] Starting to download songs. (Verbose = Off)")
                for song in songs_with_meta:
                    song_name = executor.submit(self.ytdl.download, song["result"][0]["link"], False, song)
                    temp.append(song_name)

                filenames = [
                    r.result()
                    for r in concurrent.futures.as_completed(temp)
                ]
                temp = []
                cwd = Utils.get_cwd()
                for f in filenames:
                    does_exist = executor.submit(Utils.check_file_exists, f["filename"], f)
                    temp.append(does_exist)
                exists = [
                    r.result()
                    for r in concurrent.futures.as_completed(temp)
                ]
                temp=[]
                for f in exists:
                    if not f[0]:
                        song = executor.submit(self.ytdl.download, f[1]["url"], True, f[1])
                        temp.append(song)
                for r in concurrent.futures.as_completed(temp):
                    pass

                temp=[]
                for f in exists:
                    song = executor.submit(self.ytdl.get_song_meta_by_v_id, f[1]["rest"]["result"][0]["id"], f)
                    temp.append(song)

                meta = [
                    r.result()
                    for r in concurrent.futures.as_completed(temp)
                ]
                temp=[]
                for f in meta:
                    song = executor.submit(self.ytdl.change_metadata_of_song, f["rest"][1]["filename"],f["meta"]["videoDetails"]["author"],f["meta"]["videoDetails"]["title"],f["rest"][1]["rest"]["result"][0]["thumbnails"][0]["url"])
                    temp.append(song)
                meta = [
                    r.result()
                    for r in concurrent.futures.as_completed(temp)
                ]
            console.print("""\n[bold][green][+][/green] Successfully downloaded %s song(s). \n[green][+][/green] Total song(s): %s. \n[green][>][/green] Output directory: %s.  \n[green][>][/green] [cyan]Total time needed: %.2f second(s). [/cyan]
            [/bold]""" % (len(temp)-len([e for e in exists if e[0]]), len(temp), str(self.ytdl.output_dir.absolute()), (time.time() - start_time)))



