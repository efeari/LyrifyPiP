# A class for handling Spotipy and spotify related stuff
import time
import spotipy
from threading import Lock

from spotipy.oauth2 import SpotifyOAuth

from .Track import Track
from .config import *

from .MediaHandler import MediaHandler

class SpotifyHandler(MediaHandler):
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

    def fetchNewTrack(self):
        return self.spotify.current_user_playing_track()