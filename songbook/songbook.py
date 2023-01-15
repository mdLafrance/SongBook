import re
import logging

from itertools import chain
from pathlib import Path
from typing import List

import textract

from pydantic import BaseModel, validator


_STANDARD_TUNING = "standard"
_SONG_FILE_EXTENSIONS = [
    ".txt",
    ".json",
    ".yaml",
    ".doc",
    ".docx"
]


class Song(BaseModel):
    title: str
    artist: str
    tuning: str = "standard"
    song: str

    @validator("tuning")
    def tuning_is_legal(cls, tuning: str):
        if not tuning_is_legal(tuning):
            raise ValueError(f"Illegal tuning: {tuning}")

        return tuning


def tuning_is_legal(tuning: str) -> bool:
    """Verify whether a stirng representation of a tuning is valid."""
    return bool(re.match("^([a-gA-G]{1}[b#]?){6}|standard$", tuning))


def load_song(file: Path) -> Song:
    """Create a `Song` struct from an input file."""
    if file.suffix in [".yaml", ".json"]:
        return Song.parse_file(file)

    if file.suffix == ".txt":
        with open(file, "r") as f:
            lines = f.readlines()
    elif file.suffix in [".doc", ".docx"]:
        text = textract.process(file).decode("utf-8")
        lines = text.split("\n")

    if not lines[1]:
        lines = [lines[0]] + lines[2:]

    title = lines[0].strip()
    artist = lines[1].strip()
    tuning = lines[2].strip()
    song = lines[3:]

    # If tuning was ommitted
    if not tuning_is_legal(tuning):
        tuning = _STANDARD_TUNING
        song = lines[2:]

    return Song(title=title, artist=artist, tuning=tuning, song="\n".join(song))


def load_songs_from_directory(dir: Path):
    """Attempt to load all files in directory as songs."""
    songs = []

    for file in chain.from_iterable(dir.glob(f"*{e}") for e in _SONG_FILE_EXTENSIONS):
        songs.append(load_song(file))

    return songs
