from platform import system
from .MediaHandler import MediaHandler as MediaHandler
from .Track import Track
from .config import *
import asyncio
import time
import threading

if system() == 'Windows':
    from winrt.windows.media.control import \
        GlobalSystemMediaTransportControlsSessionManager as MediaManager
    from winrt.windows.storage.streams import DataReader, Buffer, InputStreamOptions
    from io import BytesIO
    from PIL import Image

elif system() == 'Linux':
    pass

class OsMediaHandler(MediaHandler):
    def __init__(self):
        super().__init__()
        self.m_mediaInfo = None
        self.m_currentSession = None
        self._trackImg = None

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
                    self.mutex.acquire()
                    self.isPlaying = True
                    self.mutex.release()
                    if 'spotify' in sessions[i].source_app_user_model_id.lower():
                        # Give priority to Spotify
                        currentlyPlayingSessions.append([sessions[i], 0])
                    else:
                        currentlyPlayingSessions.append([sessions[i], 1])

            # Return if no currently playing session
            if len(currentlyPlayingSessions) == 0:
                self.mutex.acquire()
                self.isPlaying = False
                self.mutex.release()
                return
            
            # Order them based on the priority
            currentlyPlayingSessions.sort(key = lambda x: x[1])
            self.m_currentSession = currentlyPlayingSessions[0][0]

            info = await self.m_currentSession.try_get_media_properties_async()
            if info is None:
                return

            # song_attr[0] != '_' ignores system attributes
            info = {song_attr: info.__getattribute__(song_attr) for song_attr in dir(info) if song_attr[0] != '_'}

            # converts winrt vector to list
            info['genres'] = list(info['genres'])
            self.m_mediaInfo = info

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

            img = Image.open(binary)
            img.save(r"C:\Users\efear\Documents\VS Code Projects\Umay\TrackInfo\Background.png")
            self._trackImg = img
            
    def fetchNewTrack(self):
        t1 = threading.Thread(target=asyncio.run, args=(self.getMediaInfo(),))
        t1.start()
        t1.join()

        trackId = self.m_mediaInfo['title']
        artists = self.m_mediaInfo['artist']

        # t1 = threading.Thread(target=asyncio.run, args=(self.fetchMediaThumbnail(),))
        # t1.start()
        # t1.join()

        progressMs = self.m_currentSession.get_timeline_properties().position.duration / 10000

        self.setCurrentTrack(Track(trackId, artists, self._trackImg, None, None, progressMs))
        print('OsMediaHandler', self._currentTrack.progressMs)
        return None
    
    def checkTrackStatus(self, setCover: BackgroundChoice):
        """
        If the user is not playing a song, sets the returns TrackState.notPlaying
        If the user is playing a song which is different then the previous song, it gathers 
        the necessary information such as track ID, artis name, the album cover etc and it
        sets as the currentTrack and returns TrackState.newTrack
        If the user is still playing the same track, it updates the track progress for the parser
        and returns TrackState.updateProgress
        If the user is not playing returns TrackState.pausedTrack

        Returns:
            _type_: _description_
        """
        self.fetchNewTrack()
        if self._currentTrack is None:
            return TrackState.NOT_PLAYING
        elif self._currentTrack is not None and self._trackChanged:
            return TrackState.NEW_TRACK
        elif self._currentTrack is not None and not self._trackChanged:
            return TrackState.UPDATE_IN_PROGRESS
        # elif currentTrackTemp['is_playing'] == False:
        #     return TrackState.PAUSED_TRACK


    # def updateIsPlaying(self, isPlayingEvent):
    #     """
    #     A function called in a separate thread from main,
    #     which continously checks the status of self.isPlaying
    #     and sets the same value to isPlayingEvent to make the
    #     communication between different threads

    #     Args:
    #         isPlayingEvent (bool): A threading synchronization primitive used to
    #         detect if there is a song playing
    #     """
    #     while True:
    #         self.mutex.acquire()
    #         self.fetchNewTrack()
    #         if self._currentTrack is None:
    #             self.isPlaying = False
    #             isPlayingEvent.clear()
    #         else:
    #             self.isPlaying = True
    #             isPlayingEvent.set()
    #         self.mutex.release()
    #         time.sleep(CONST_CHECK_IS_PLAYING_FREQUENCY)