# A data class to hold track ID, img and lyrics location

from dataclasses import dataclass

@dataclass
class Track:
    name: str
    artists: str
    img: str
    lyrics: str
    progressMs: float
    id: str

    def __init__(self, name: str = " ", artists: str = " ", img: str = " ", id: str = " ", lyrics: str = " ", progressMs: float = 0):
        self.name = name
        self.artists = artists
        self.img = img
        self.lyrics = lyrics
        self.progressMs = progressMs
        self.id = id

    def __eq__(self, rhs):
        return (rhs is not None and self.name == rhs.name and self.artists == rhs.artists)