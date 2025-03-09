import asyncio

from .Track import Track
from .config import *

class MediaHandler:
    def __init__(self, on_track_change_callback, _on_albumcover_change_callback):
        self._currentTrack = Track(None, None, None, None, None, None)
        self._previousTrack = None  # To track changes
        self._on_track_change_callback = on_track_change_callback 
        self._on_albumcover_change_callback = _on_albumcover_change_callback
        self._track_img = None
        self._event_loop = asyncio.get_event_loop()
        self.is_playing = False
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
    
    def stop_monitoring(self):
        raise NotImplementedError()

    def __del__(self):
        self.stop_monitoring()
    