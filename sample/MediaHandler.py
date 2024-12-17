from .Track import Track
import requests
from .config import *
import time

class MediaHandler:
    def __init__(self):
        self._currentTrack = Track
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

    def fetchNewTrack(self):
        raise NotImplementedError()
    
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
        currentTrackTemp = self.fetchNewTrack()
        if currentTrackTemp is None:
            return TrackState.NOT_PLAYING
        elif currentTrackTemp is not None and currentTrackTemp['item']['id'] != self._currentTrack.id:
            trackId = currentTrackTemp["item"]["name"]
            artists = currentTrackTemp["item"]["artists"]
            artists = " ".join([artist["name"] for artist in artists])
            id = currentTrackTemp['item']['id']
            trackImg = currentTrackTemp["item"]["album"]["images"][0]["url"]
            if setCover == BackgroundChoice.ALBUM_COVER:
                img_data = requests.get(trackImg).content
                with open('TrackInfo\Background.png', 'wb') as handler:
                    handler.write(img_data)           
            progressMs = currentTrackTemp["progress_ms"]
            self.setCurrentTrack(Track(trackId, artists, trackImg, id, None, progressMs))
            return TrackState.NEW_TRACK
        elif currentTrackTemp['is_playing'] and currentTrackTemp['item']['id'] == self._currentTrack.id:
            self._currentTrack.progressMs = currentTrackTemp["progress_ms"]
            return TrackState.UPDATE_IN_PROGRESS
        elif currentTrackTemp['is_playing'] == False:
            return TrackState.PAUSED_TRACK
        
    def updateIsPlaying(self, isPlayingEvent):
        """
        A function called in a separate thread from main,
        which continously checks the status of self.isPlaying
        and sets the same value to isPlayingEvent to make the
        communication between different threads

        Args:
            isPlayingEvent (bool): A threading synchronization primitive used to
            detect if there is a song playing
        """
        while True:
            self.mutex.acquire()
            if self.fetchNewTrack() is None:
                self.isPlaying = False
                isPlayingEvent.clear()
            else:
                self.isPlaying = True
                isPlayingEvent.set()
            self.mutex.release()
            time.sleep(CONST_CHECK_IS_PLAYING_FREQUENCY)