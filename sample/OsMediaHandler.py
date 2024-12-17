from platform import system
from .Track import Track
if system() == 'Windows':
    from winrt.windows.media.control import \
        GlobalSystemMediaTransportControlsSessionManager as MediaManager
    from winrt.windows.storage.streams import DataReader, Buffer, InputStreamOptions
    from io import BytesIO
    from PIL import Image

elif system() == 'Linux':
    pass

class OsMediaHandler:
    def __init__(self):
        self.m_mediaInfo = None
        self.m_currentSession = None
        pass

    async def fetchMediaThumbnail(self):
        if self.m_mediaInfo['thumbnail']:
            thumb_stream_ref = self.m_mediaInfo['thumbnail']
            thumb_read_buffer = Buffer(5000000)

            readable_stream = await thumb_stream_ref.open_read_async()
            await readable_stream.read_async(thumb_read_buffer, thumb_read_buffer.capacity, InputStreamOptions.READ_AHEAD)

            buffer_reader = DataReader.from_buffer(thumb_read_buffer)
            byte_buffer = buffer_reader.read_bytes(thumb_read_buffer.length)

            binary = BytesIO()
            binary.write(bytearray(byte_buffer))
            binary.seek(0)
            print(len(bytearray(byte_buffer)))

            img = Image.open(binary)
            img.save(r"C:\Users\efear\Documents\VS Code Projects\Umay\TrackInfo\Background.png")

            return img

    async def fetchNewTrack(self):
        await self.getMediaInfo()
        trackId = self.m_mediaInfo['title']
        artists = self.m_mediaInfo['artist']
        trackImg = await self.fetchMediaThumbnail()
        progressMs = self.m_currentSession.get_timeline_properties().position.duration / 10000

        #self.setCurrentTrack(Track(trackId, artists, trackImg, None, None, progressMs))
        return None
    
    async def getMediaInfo(self):
        if system() == 'Windows':
            mediaManager = await MediaManager.request_async()
            # Get current media sessions
            sessions = mediaManager.get_sessions()

            # Find which ones are playing
            currentlyPlayingSessions = []
            for i in range(len(sessions)):
                # https://learn.microsoft.com/en-us/uwp/api/windows.media.control.globalsystemmediatransportcontrolssessionplaybackstatus?view=winrt-26100
                if sessions[i].get_playback_info().playback_status == 4:
                    if 'spotify' in sessions[i].source_app_user_model_id.lower():
                        # Give priority to Spotify
                        currentlyPlayingSessions.append([sessions[i], 0])
                    else:
                        currentlyPlayingSessions.append([sessions[i], 1])

            # Return if no currently playing session
            if len(currentlyPlayingSessions) == 0:
                return
            
            # Order them based on the priority
            currentlyPlayingSessions.sort(key = lambda x: x[1])
            self.m_currentSession = currentlyPlayingSessions[0][0]

            info = await self.m_currentSession.try_get_media_properties_async()

            # song_attr[0] != '_' ignores system attributes
            info = {song_attr: info.__getattribute__(song_attr) for song_attr in dir(info) if song_attr[0] != '_'}

            # converts winrt vector to list
            info['genres'] = list(info['genres'])
            self.m_mediaInfo = info