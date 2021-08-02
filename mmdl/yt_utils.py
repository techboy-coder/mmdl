from __future__ import unicode_literals
from .utils import Utils
import youtube_dl
from youtubesearchpython.__future__ import VideosSearch
from ytmusicapi import YTMusic
YTMusic = YTMusic()
from pathlib import Path
import os
import eyed3
import urllib
from .globals import console


class YtdlUtils():
    def __init__(self, mmdl: bool):

        self.debug = mmdl.debug
        self.verbose = mmdl.verbose
        self.output_dir = Path(Utils.get_cwd()+"/music")
        self.ytdl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [
                {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                # 'preferredquality': '192',
                }
            ],
            'outtmpl': str(self.output_dir)+'/%(title)s.%(ext)s',
            'quiet': True,
            'ignoreerrors': True,
            "logger":self.logger(),
            'progress_hooks': [self.progress_hook()],
            'restrictfilenames':True,
            'forcefilename':True,
        }

    def download(self, url: str, do_download: bool, rest: None):
        if do_download:
            with youtube_dl.YoutubeDL(self.ytdl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                return {"filename": filename, "url": url, "rest":rest}
        else:
            with youtube_dl.YoutubeDL(self.ytdl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                filename = ydl.prepare_filename(info)
                return {"filename": filename, "url": url, "rest":rest}
            
    def logger(self):
        debug = self.debug
        class Logger(object):
            def debug(self, msg):
                Utils.log_handler(debug, msg, "debug")
            def warning(self, msg):
                Utils.log_handler(debug, msg, "warning")

            def error(self, msg):
                Utils.log_handler(debug, msg, "error")

        return Logger()
    
    def progress_hook(self):
        verbose = self.verbose
        def hook(d):

            pass

        return hook
    def clear_cache(self):
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            try:
                if self.debug:
                    Utils.blockPrint()
                    ydl.cache.remove()
                    Utils.enablePrint()
                else:
                    ydl.cache.remove()
            except Exception as e:
                Utils.log_handler(self.debug, e, "error")
    
    async def find_song_on_yt(self, title: str):
        return VideosSearch(title, limit = 2).next()
    
    def get_song_meta_by_v_id(self, id, rest: None):
        return {"meta":YTMusic.get_song(id),"rest":rest}
    
    def change_metadata_of_song(self, filepath, artist, song_title, thumbnail_url):
        try:
            audiofile = eyed3.load(filepath)
            audiofile.tag.artist = artist
            audiofile.tag.title = song_title
            response = urllib.request.urlopen(thumbnail_url)  
            imagedata = response.read()
            audiofile.tag.images.set(3, imagedata , "image/jpeg" ,"Description")
            audiofile.tag.save()
        except Exception as e:
            Utils.log_handler(self.debug, e, "error")
        return filepath
