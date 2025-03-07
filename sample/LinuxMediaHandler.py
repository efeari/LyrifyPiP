import subprocess
import time
import asyncio

from .MediaHandler import MediaHandler as MediaHandler

class WinMediaHandler(MediaHandler):
    def __init__(self, on_track_change_callback=None, _on_albumcover_change_callback=None):
        super().__init__()
        self._m_mediaInfo = None
        self._m_current_session = None
        self._track_img = None
        self._event_loop = asyncio.get_event_loop()
        self._timeline_changed_token = None
        self._on_track_change_callback = on_track_change_callback 
        self._on_albumcover_change_callback = _on_albumcover_change_callback
    
    async def start_monitoring(self):
        process = subprocess.Popen(
        ["playerctl", "--follow", "metadata", "--format", "{{artist}}"],
        stdout=subprocess.PIPE,
        text=True
    )