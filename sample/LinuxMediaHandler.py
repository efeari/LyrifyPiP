from platform import system
import time
import asyncio
import threading
if system() == 'Linux':
    import subprocess

from .config import *
from .MediaHandler import MediaHandler as MediaHandler
from .Track import Track

class LinuxMediaHandler(MediaHandler):
    def __init__(self, on_track_change_callback=None, _on_albumcover_change_callback=None):
        super().__init__(on_track_change_callback, _on_albumcover_change_callback)
        self._running = False
        self._monitor_thread = None
        self._process = None

    async def start_monitoring(self):
            self._running = True
            asyncio.create_task(self._create_subprocess())
            self._monitor_thread = threading.Thread(target=self._start_track_monitoring, daemon=True)
            self._monitor_thread.start()
            # Keep the async task alive
            await asyncio.Event().wait()

    async def _create_subprocess(self):
        """Continuously listen for song and position changes."""
        self._process = subprocess.Popen(
            ["playerctl", "--follow", "metadata", "--format", "{{artist}}"],
            stdout=subprocess.PIPE,
            text=True
        )

    def _update_current_track(self):
        if self._process is None:
            self.set_current_track(None)
            return
        
        try:
            if subprocess.check_output(["playerctl", "status"], text=True).strip() == "Playing":
                self.is_playing = True 
            else: 
                self.is_playing = False

            artists = subprocess.check_output(["playerctl", "metadata", "--format", "{{artist}}"], text=True).strip()
            track_id = subprocess.check_output(["playerctl", "metadata", "--format", "{{title}}"], text=True).strip()
            progress = subprocess.check_output(["playerctl", "position"], text=True).strip()
            progress_ms = int(float(progress) * 1000)
            new_track = Track(track_id, artists, self._track_img, None, None, progress_ms)
            self.set_current_track(new_track)
        
        except subprocess.CalledProcessError:
            return
        
        # Notify main via callback
        if self._on_track_change_callback:
            asyncio.run_coroutine_threadsafe(
                self._on_track_change_callback(self.get_current_track()), 
                self._event_loop
            )


    def _start_track_monitoring(self):
        """Run _update_current_track every 2 seconds in a separate thread."""
        while self._running:
            self._update_current_track()
            time.sleep(CONST_DEFAULT_UPDATE_TRACK_FREQUENCY)

    def stop_monitoring(self):
        """Stop the monitoring thread."""
        self._running = False
        if self._process:
            self._process.terminate()
        if self._monitor_thread:
            self._monitor_thread.join()