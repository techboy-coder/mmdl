from __future__ import unicode_literals
from lxml.cssselect import CSSSelector
from lxml.html import fromstring
import questionary
from rich import print, pretty
from rich.traceback import install
install()
pretty.install()
from rich.progress import track
from rich.console import Console
from rich.prompt import Prompt
console = Console()


def asker():
    try:
        single_songs = questionary.select(
            "How many songs do you want to download?",
            choices=[
                "One song",
                "Multiple Songs"
            ]
        ).ask()

        if single_songs == "One song":
            return [questionary.text("What is the song name").ask()]
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
                file = questionary.path("Where is that file located?").ask()
                with open(file, "r", encoding="utf-8") as f:
                    data = f.read()
                h = fromstring(data)
                sel = CSSSelector("yt-formatted-string.title.style-scope.ytmusic-responsive-list-item-renderer.complex-string > a.yt-simple-endpoint.style-scope.yt-formatted-string")
                songs_list=[e.text for e in sel(h)]
                return songs_list

            elif input_method=="List in textfile (1 Song per line)":
                file = questionary.path("Where is that file located?").ask()
                text_file = open(file ,encoding='utf-8')
                songs_list = text_file.read().splitlines()
                return songs_list
            elif input_method=="Songs, comma seperated":
                songs_list = questionary.text("Write all songs (comma seperated)").ask().split(",")
                return songs_list
    except Exception as e:
        ## eventually change :/
        pass