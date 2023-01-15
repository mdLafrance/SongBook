import sys

from pathlib import Path

from rich import print

from songbook.songbook import load_songs_from_directory, load_song

print(load_songs_from_directory(Path(sys.argv[1])))
