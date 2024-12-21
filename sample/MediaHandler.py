from .Track import Track
from .config import *
from threading import Lock

class MediaHandler:
    def __init__(self):
        self._currentTrack = Track(None, None, None, None, None, None)
        self._trackChanged = False
        self.mutex = Lock()
        self.mutex.acquire()
        self.isPlaying = False
        self.mutex.release()
        pass
    
    def getCurrentTrack(self):
        """
        Getter for the _currentTrack

        Returns:
            self_currentTrack: Current playing track
        """
        return self._currentTrack
    
    def setCurrentTrack(self, newTrack: Track):
        """
        Setter for the _current track

        Args:
            newTrack (Track): _currentTrack to be
        """
        if (self._currentTrack != newTrack):
            self._trackChanged = True
        else:
            self._trackChanged = False

        self._currentTrack = newTrack

    def fetchNewTrack(self):
        raise NotImplementedError()
    
    def checkTrackStatus(self, setCover: BackgroundChoice):
        raise NotImplementedError()
    
    