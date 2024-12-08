# A class for handling Spotipy and spotify related stuff
import time
import spotipy
import requests
from threading import Lock

from spotipy.oauth2 import SpotifyOAuth

from .Track import Track
from .config import *

class SpotifyHandler():
    def __init__(self):
        """
        Constructor for SpotifyHandler, which is the main class handling the
        API connection via Spotipy
        """
        self.scope = "user-read-currently-playing, user-read-playback-state"
        self.spotify = None
        self._currentTrack = Track(None, None, None, None, None, None)
        self.initSpotipy()
        self.mutex = Lock()
        self.mutex.acquire()
        self.isPlaying = False
        self.mutex.release()

    # Function for initalization of the class
    # Also reused if we lose the token
    def initSpotipy(self):
        """
        A function for initializing Spotipy and the authManager to handle the connection
        to Spotify API
        """
        if (AUTH_FLOW == AuthFlow.AUTHORIZATION_CODE_FLOW):
            self.authManager = SpotifyOAuth(
                scope=self.scope,
                redirect_uri=SPOTIPY_REDIRECT_URI,
                client_id=SPOTIPY_CLIENT_ID,
                client_secret=SPOTIPY_CLIENT_SECRET,
                username=SPOTIPY_USERID)
            self.spotify = spotipy.Spotify(auth_manager=self.authManager)

    # Refreshes Spotify token if its expired
    def refreshSpotify(self, isPlayingEvent):
        """
        A function to refresh the Spotify API token if exprired
        If there is a song playing, the function enters a continous loop untill
        isPlayingEvent becomes false.
        Inside the loop, every CONST_DEFAFULT_TOKEN_REFRESH_FREQUENCY ms
        it checks if the token is expired and if it is, it refreshes the token
        Args:
            isPlayingEvent (bool): A threading synchronization primitive used to
            detect if there is a song playing
        """
        if (AUTH_FLOW == AuthFlow.AUTHORIZATION_CODE_FLOW):
            isPlayingEvent.wait()
            while isPlayingEvent.is_set():
                tokenInfo = self.authManager.cache_handler.get_cached_token()
                if self.authManager.is_token_expired(tokenInfo):
                    self.initSpotipy()
                if self.isPlaying:
                    time.sleep(CONST_DEFAFULT_TOKEN_REFRESH_FREQUENCY)
                else:
                    isPlayingEvent.wait()
    
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

    def checkTrackStatus(self):
        """
        A function to handle the track status via Spotify API
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
        currentTrackTemp = self.spotify.current_user_playing_track()
        if currentTrackTemp is None:
            return TrackState.NOT_PLAYING
        elif currentTrackTemp is not None and currentTrackTemp['item']['id'] != self._currentTrack.id:
            trackId = currentTrackTemp["item"]["name"]
            artists = currentTrackTemp["item"]["artists"]
            artists = " ".join([artist["name"] for artist in artists])
            id = currentTrackTemp['item']['id']
            trackImg = currentTrackTemp["item"]["album"]["images"][0]["url"]
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
            if self.spotify.current_user_playing_track() is None:
                self.isPlaying = False
                isPlayingEvent.clear()
            else:
                self.isPlaying = True
                isPlayingEvent.set()
            self.mutex.release()
            time.sleep(CONST_CHECK_IS_PLAYING_FREQUENCY)