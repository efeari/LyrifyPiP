from .Track import Track
from .config import *

class MediaHandler:
    def __init__(self):
        self._currentTrack = Track(None, None, None, None, None, None)
        self._previousTrack = None  # To track changes
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
        self._currentTrack = newTrack

    def getPreviousTrack(self):
        """
        Getter for the _prev

        Returns:
            _previousTrack: Current playing track
        """
        return self._previousTrack
    
    def setPreviousTrack(self, previousTrack: Track):
        """
        Setter for the _prev track

        Args:
            previousTrack (Track): _prev track to be
        """
        if (self._previousTrack != previousTrack):
            self._previousTrack = previousTrack

    def fetchNewTrack(self):
        raise NotImplementedError()
    
    def checkTrackStatus(self, setCover: BackgroundChoice):
        raise NotImplementedError()
    
    