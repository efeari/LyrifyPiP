import re
from numpy import asarray

import syncedlyrics

from .helpers import *
from .Track import Track

class LyricHandler:
    def __init__(self):
        self._currentTrack = Track(None, None, None, None, None, None)
        self.m_trackFound = False

    def setCurrentTrack(self, newTrack):
        # If the user changed the song, we need to reparse all the lyrics
        if self._currentTrack != newTrack:
            self._currentTrack = newTrack
            searchTerm = " ".join({self._currentTrack.name, self._currentTrack.artists})
            self.lastTimeIndex = 0
            try:
                self.lryics = syncedlyrics.search(searchTerm)
            except Exception as e:
                self.lryics = None
            self.firstTimeStamp = 0
            # If we have matched lyrics!
            if self.lryics is not None:
                self.getParsedLyrics()
                self.m_trackFound = True
                self.lastTimeIndex = self._currentTrack.progressMs
                return self.matchCurrentLine()
            else:
                self.m_trackFound = False
                return None
        # Means that user is still playing the last parsed song
        # but we still need to find the correct lyric in the dict!
        else:
            if self.m_trackFound:
                self._currentTrack = newTrack
                self.lastTimeIndex = self._currentTrack.progressMs
                return self.matchCurrentLine()
            else:
                return None

    def getParsedLyrics(self):
            lines = self.lryics.split('\n')
            self.parsedLyrics = {}
            self.timeMs = []

            for line in lines:
                line = line.strip()
                if line and line.startswith("["):
                    parsed_line = self.parseLine(line)
                    if parsed_line:
                        time_str, verse_text = parsed_line
                        inMs = reformatToMilliSecond(int(time_str[0]) * 10 + int(time_str[1]), int(time_str[3]) * 10 + int(time_str[4]), int(time_str[6]) * 10 + int(time_str[7]))
                        # So we store the first timestamp of the lyric in this variable for later use
                        if not bool(self.parsedLyrics):
                            self.firstTimeStamp = inMs
                        # So we use the parsedLyrics which is a dict with one key (timestamp) and 2 values (corresponding lyric and whether it is already parsed or not)
                        # Will be used temporarly might change in the future
                        self.parsedLyrics[inMs] =  [verse_text, False]
                        
    def parseLine(self, line):
        pattern = r'\[(\d{2}:\d{2}\.\d{2})\](.+)'
        match = re.match(pattern, line)

        if match:
            time_str = match.group(1)
            verse_text = match.group(2).strip()
            return time_str, verse_text

        else:
            return None
    
    # A function to return/print the corresponding lyric
    def matchCurrentLine(self):
        # If the index is 0 or if we did not hit the first lyric yet
        if self.lastTimeIndex == 0 or self.lastTimeIndex <= self.firstTimeStamp:
            return None
        else:
            try:
                key = self.closestTimeStamp(self.lastTimeIndex)
                keys = list(self.parsedLyrics.keys())
                keyIndex = keys.index(key)
                if self.parsedLyrics[key][1] is False:
                    self.parsedLyrics[key][1] = True
                    if keyIndex == 0:
                        return self.parsedLyrics[key][0] + "\n" + "\n" + self.parsedLyrics[keys[keyIndex + 1]][0]
                    elif keyIndex == len(keys) - 1:
                        return self.parsedLyrics[keys[keyIndex - 1]][0] + "\n"+ "\n" + self.parsedLyrics[key][0]
                    else:
                        return self.parsedLyrics[keys[keyIndex - 1]][0] + "\n"+ "\n" + \
                            self.parsedLyrics[key][0] + "\n" + "\n" + \
                            self.parsedLyrics[keys[keyIndex + 1]][0]
            except:
                return ""

    # A small helper function to match the exact lyric
    def closestTimeStamp(self, currentStamp):
        array = asarray(list(self.parsedLyrics.keys()))
        idx = array[array <= currentStamp].argmax()
        return array[idx]
        