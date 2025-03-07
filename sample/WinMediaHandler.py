from platform import system
from .MediaHandler import MediaHandler as MediaHandler
from .Track import Track
from .config import *
import asyncio
from winrt.windows.media.control import \
    GlobalSystemMediaTransportControlsSessionManager as MediaManager
from winrt.windows.storage.streams import DataReader, Buffer, InputStreamOptions
from io import BytesIO
from PIL import Image

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
        asyncio.create_task(self._setup_session_manager())
        await asyncio.Event().wait()

    async def _setup_session_manager(self):
        media_manager = await MediaManager.request_async()
        self._m_current_session = await self._get_current_session(media_manager)
        if self._m_current_session:
            asyncio.create_task(self._subscribe_to_changes())
            asyncio.create_task(self._fetch_initial_media_info())

    async def _get_current_session(self, media_manager):
        sessions = media_manager.get_sessions()
        currently_playing = []
        for session in sessions:
            playback_info = session.get_playback_info()
            if playback_info and playback_info.playback_status == 4:
                self.is_playing = True
                priority = 0 if "spotify" in session.source_app_user_model_id.lower() else 1
                currently_playing.append((session, priority))
        if not currently_playing:
            self.is_playing = False
            return None
        currently_playing.sort(key=lambda x: x[1])
        return currently_playing[0][0]

    async def _subscribe_to_changes(self):
        if self._m_current_session and not self._timeline_changed_token:
            self._timeline_changed_token = self._m_current_session.add_timeline_properties_changed(
                lambda s, e: self._event_loop.call_soon_threadsafe(self._on_timeline_changed)
            )

    async def _fetch_initial_media_info(self):
        await self.get_media_info()
        if self._m_mediaInfo:
            asyncio.create_task(self.fetch_media_thumbnail())
            self._update_current_track()

    async def get_media_info(self):
        if not self._m_current_session:
            self._m_mediaInfo = None
            return
        info = await self._m_current_session.try_get_media_properties_async()
        if info is None:
            self._m_mediaInfo = None
            return
        self._m_mediaInfo = {
            attr: getattr(info, attr) for attr in dir(info) if not attr.startswith("_")
        }
        self._m_mediaInfo["genres"] = list(self._m_mediaInfo["genres"])

    async def fetch_media_thumbnail(self):
        if not self._m_mediaInfo or not self._m_mediaInfo.get("thumbnail"):
            self._track_img = None
            return
        thumb_stream_ref = self._m_mediaInfo["thumbnail"]
        thumb_read_buffer = Buffer(5000000)
        readable_stream = await thumb_stream_ref.open_read_async()
        await readable_stream.read_async(
            thumb_read_buffer, thumb_read_buffer.capacity, InputStreamOptions.READ_AHEAD
        )
        buffer_reader = DataReader.from_buffer(thumb_read_buffer)
        byte_buffer = buffer_reader.read_bytes(thumb_read_buffer.length)
        with BytesIO(bytearray(byte_buffer)) as binary:
            self._track_img = Image.open(binary)
            self._track_img.save("TrackInfo\Background.png")

        # Notify main via callback
        if self._on_albumcover_change_callback:
            asyncio.run_coroutine_threadsafe(
                self._on_albumcover_change_callback(), 
                self._event_loop
            )

    def _update_current_track(self):
        if not self._m_mediaInfo or not self._m_current_session:
            self.set_current_track(None)
            return
        track_id = self._m_mediaInfo.get("title", "Unknown")
        artists = self._m_mediaInfo.get("artist", "Unknown")
        progress_ms = self._m_current_session.get_timeline_properties().position.duration / 10000
        new_track = Track(track_id, artists, self._track_img, None, None, progress_ms)
        self.set_current_track(new_track)
        
        # Notify main via callback
        if self._on_track_change_callback:
            asyncio.run_coroutine_threadsafe(
                self._on_track_change_callback(self.get_current_track()), 
                self._event_loop
            )

    def _on_timeline_changed(self):
        asyncio.run_coroutine_threadsafe(self._handle_timeline_change(), self._event_loop)

    async def _handle_timeline_change(self):
        await self.get_media_info()
        if self._m_mediaInfo:
            self._update_current_track()
            if (self._previousTrack != self._currentTrack): 
                asyncio.create_task(self.fetch_media_thumbnail())


    def stop_monitoring(self):
        if self._m_current_session and self._timeline_changed_token:
            self._m_current_session.remove_timeline_properties_changed(self._timeline_changed_token)
            self._timeline_changed_token = None
