from enum import Enum

TrackState = Enum('TrackState', ['NEW_TRACK', 'UPDATE_IN_PROGRESS', 'PAUSED_TRACK', 'NOT_PLAYING'])
BackgroundChoice = Enum('BackgroundChoice', ['ALBUM_COVER', 'COLOR'])

alphaValue = 200
resolutionToTextRatio = 30

CONST_DEFAULT_UPDATE_TRACK_FREQUENCY = 0.3
CONST_LYRICS_PROVIDER = "Musixmatch"


