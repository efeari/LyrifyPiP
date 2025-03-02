import sample.LyricHandler as LyricHandler
import sample.ScreenHandler as ScreenHandler
import sample.config as config
import sample.OsMediaHandler as OsMediaHandler
from .config import *

class LyrifyPiP:
    def __init__(self, sys_argv):
        if len(sys_argv) > 1:
            try:
                print(f"Arguments passed: {sys_argv[1:]}")
                self.screen_handler = ScreenHandler.ScreenHandler(int(sys_argv[1]), int(sys_argv[2]), config.BackgroundChoice(sys_argv[3]))
            except ValueError:
                print("Invalid screen dimensions provided")
                return -1
        else:
            self.screen_handler = ScreenHandler.ScreenHandler()
        
        self.lyric_handler = LyricHandler.LyricHandler()
        self.media_handler = OsMediaHandler.OsMediaHandler(on_track_change_callback=self.on_track_change, 
                                        _on_albumcover_change_callback=self.on_albumcover_change)

    async def on_track_change(self, track):
        lyrics = self.lyric_handler.setCurrentTrack(track)
        currentState = config.TrackState.NOT_PLAYING
        if track == None:
            currentState = config.TrackState.NOT_PLAYING
        elif track and self.media_handler.isPlaying == False:
            currentState = config.TrackState.PAUSED_TRACK
        elif track and track != self.media_handler.getPreviousTrack():
            currentState = config.TrackState.NEW_TRACK
            self.media_handler.setPreviousTrack(self.media_handler.getCurrentTrack())
        elif track and track == self.media_handler.getPreviousTrack():
            currentState = config.TrackState.UPDATE_IN_PROGRESS

        self.screen_handler.updateScreen(currentState, lyrics)
        self.screen_handler.update()

    async def on_albumcover_change(self):
        if (self.screen_handler.getBackgroundChoice == config.BackgroundChoice.ALBUM_COVER):
            self.screen_handler.updateAlbumCover()

    async def run(self):
        try:
            await self.media_handler.start_monitoring()
        except KeyboardInterrupt:
            self.media_handler.stop_monitoring()
