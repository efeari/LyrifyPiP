from .Track import Track
from .config import *

class MediaHandler:
    def __init__(self):
        self._currentTrack = Track(None, None, None, None, None, None)
        self._previousTrack = None  # To track changes
        pass
    
    def get_current_track(self):
        """
        Getter for the _currentTrack

        Returns:
            self_currentTrack: Current playing track
        """
        return self._currentTrack
    
    def set_current_track(self, newTrack: Track):
        """
        Setter for the _current track

        Args:
            newTrack (Track): _currentTrack to be
        """
        self._currentTrack = newTrack

    def get_previous_track(self):
        """
        Getter for the _prev

        Returns:
            _previousTrack: Current playing track
        """
        return self._previousTrack
    
    def set_previous_track(self, previousTrack: Track):
        """
        Setter for the _prev track

        Args:
            previousTrack (Track): _prev track to be
        """
        if (self._previousTrack != previousTrack):
            self._previousTrack = previousTrack

    def fetch_new_track(self):
        raise NotImplementedError()
    
    def check_track_status(self, setCover: BackgroundChoice):
        raise NotImplementedError()
    
    async def start_monitoring(self):
        raise NotImplementedError()
    