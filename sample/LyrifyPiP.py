from platform import system

import sample.LyricHandler as LyricHandler
import sample.ScreenHandler as ScreenHandler
import sample.config as config
import sample.WinMediaHandler as WinMediaHandler
import sample.LinuxMediaHandler as LinuxMediaHandler
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

        if system() == 'Windows':
            self.media_handler = WinMediaHandler.WinMediaHandler(on_track_change_callback=self.on_track_change, 
                                        _on_albumcover_change_callback=self.on_albumcover_change)
        elif system() == 'Linux':
            self.media_handler = LinuxMediaHandler.LinuxMediaHandler(on_track_change_callback=self.on_track_change, 
                                        _on_albumcover_change_callback=self.on_albumcover_change)
        else:
            raise NotImplementedError(f"Unsupported OS: {system()}")
        
        self.lyric_handler = LyricHandler.LyricHandler()
        

    async def on_track_change(self, track):
        lyrics = self.lyric_handler.set_current_track(track)
        current_state = config.TrackState.NOT_PLAYING
        if track == None:
            current_state = config.TrackState.NOT_PLAYING
        elif track and self.media_handler.is_playing == False:
            current_state = config.TrackState.PAUSED_TRACK
        elif track and track != self.media_handler.get_previous_track():
            current_state = config.TrackState.NEW_TRACK
            self.media_handler.set_previous_track(self.media_handler.get_current_track())
        elif track and track == self.media_handler.get_previous_track():
            current_state = config.TrackState.UPDATE_IN_PROGRESS

        self.screen_handler.update_screen(current_state, lyrics)
        self.screen_handler.update()

    async def on_albumcover_change(self):
        if (self.screen_handler.get_background_choice == config.BackgroundChoice.ALBUM_COVER):
            self.screen_handler.update_album_cover()

    async def run(self):
        try:
            await self.media_handler.start_monitoring()
        except KeyboardInterrupt:
            self.media_handler.stop_monitoring()
