from .Track import Track
from .config import BackgroundChoice

class MediaHandler:
    def __init__(self):
        pass
    
    def getCurrentTrack(self):
        raise NotImplementedError()
    
    def setCurrentTrack(self, newTrack: Track):
        raise NotImplementedError()

    def checkTrackStatus(self, setCover: BackgroundChoice):
        raise NotImplementedError()
        
    def updateIsPlaying(self, isPlayingEvent):
        raise NotImplementedError()