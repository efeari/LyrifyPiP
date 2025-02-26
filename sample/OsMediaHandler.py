from platform import system
from .MediaHandler import MediaHandler as MediaHandler
from .Track import Track
from .config import *
import asyncio

if system() == 'Windows':
    from winrt.windows.media.control import \
        GlobalSystemMediaTransportControlsSessionManager as MediaManager
    from winrt.windows.storage.streams import DataReader, Buffer, InputStreamOptions
    from io import BytesIO
    from PIL import Image

elif system() == 'Linux':
    pass

class OsMediaHandler(MediaHandler):
    def __init__(self, on_track_change_callback=None):
        super().__init__()
        self.m_mediaInfo = None
        self.m_currentSession = None
        self._trackImg = None
        self._event_loop = asyncio.get_event_loop()
        self._timeline_changed_token = None
        self._on_track_change_callback = on_track_change_callback  # Callback for main

    async def start_monitoring(self):
        #print("Starting media monitoring...")
        await self._setup_session_manager()
        await asyncio.Event().wait()

    async def _setup_session_manager(self):
        media_manager = await MediaManager.request_async()
        self.m_currentSession = await self._get_current_session(media_manager)
        if self.m_currentSession:
            await self._subscribe_to_changes()
            await self._fetch_initial_media_info()

    async def _get_current_session(self, media_manager):
        sessions = media_manager.get_sessions()
        currently_playing = []
        for session in sessions:
            playback_info = session.get_playback_info()
            if playback_info and playback_info.playback_status == 4:
                self.isPlaying = True
                priority = 0 if "spotify" in session.source_app_user_model_id.lower() else 1
                currently_playing.append((session, priority))
        if not currently_playing:
            self.isPlaying = False
            return None
        currently_playing.sort(key=lambda x: x[1])
        return currently_playing[0][0]

    async def _subscribe_to_changes(self):
        if self.m_currentSession and not self._timeline_changed_token:
            self._timeline_changed_token = self.m_currentSession.add_timeline_properties_changed(
                lambda s, e: self._event_loop.call_soon_threadsafe(self._on_timeline_changed)
            )
            #print("Subscribed to timeline changes.")

    async def _fetch_initial_media_info(self):
        await self.getMediaInfo()
        if self.m_mediaInfo:
            await self.fetchMediaThumbnail()
            self._update_current_track()

    async def getMediaInfo(self):
        if not self.m_currentSession:
            self.m_mediaInfo = None
            return
        info = await self.m_currentSession.try_get_media_properties_async()
        if info is None:
            self.m_mediaInfo = None
            return
        self.m_mediaInfo = {
            attr: getattr(info, attr) for attr in dir(info) if not attr.startswith("_")
        }
        self.m_mediaInfo["genres"] = list(self.m_mediaInfo["genres"])
        #print(f"Media info updated: {self.m_mediaInfo['title']} by {self.m_mediaInfo['artist']}")

    async def fetchMediaThumbnail(self):
        if not self.m_mediaInfo or not self.m_mediaInfo.get("thumbnail"):
            self._trackImg = None
            return
        thumb_stream_ref = self.m_mediaInfo["thumbnail"]
        thumb_read_buffer = Buffer(5000000)
        readable_stream = await thumb_stream_ref.open_read_async()
        await readable_stream.read_async(
            thumb_read_buffer, thumb_read_buffer.capacity, InputStreamOptions.READ_AHEAD
        )
        buffer_reader = DataReader.from_buffer(thumb_read_buffer)
        byte_buffer = buffer_reader.read_bytes(thumb_read_buffer.length)
        with BytesIO(bytearray(byte_buffer)) as binary:
            self._trackImg = Image.open(binary)
            self._trackImg.save(r"C:\Users\efear\Documents\VS Code Projects\Umay\TrackInfo\Background.png")
        #print("Thumbnail fetched and saved.")

    def _update_current_track(self):
        if not self.m_mediaInfo or not self.m_currentSession:
            self.setCurrentTrack(None)
            return
        track_id = self.m_mediaInfo.get("title", "Unknown")
        artists = self.m_mediaInfo.get("artist", "Unknown")
        progress_ms = self.m_currentSession.get_timeline_properties().position.duration / 10000
        new_track = Track(track_id, artists, self._trackImg, None, None, progress_ms)
        self.setPreviousTrack(self.getCurrentTrack())
        self.setCurrentTrack(new_track)
        print(f"Current track updated: {track_id} - Progress: {progress_ms}ms")
        
        # Notify main via callback
        if self._on_track_change_callback:
            asyncio.run_coroutine_threadsafe(
                self._on_track_change_callback(self.getCurrentTrack()), 
                self._event_loop
            )

    def _on_timeline_changed(self):
        #print("Timeline properties changed detected.")
        asyncio.run_coroutine_threadsafe(self._handle_timeline_change(), self._event_loop)

    async def _handle_timeline_change(self):
        await self.getMediaInfo()
        if self.m_mediaInfo:
            await self.fetchMediaThumbnail()
            self._update_current_track()

    def stop_monitoring(self):
        if self.m_currentSession and self._timeline_changed_token:
            self.m_currentSession.remove_timeline_properties_changed(self._timeline_changed_token)
            self._timeline_changed_token = None
            #print("Unsubscribed from timeline changes.")