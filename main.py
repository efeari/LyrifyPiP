import time
import threading
import sys

import sample.SpotifyHandler as SpotifyHandler
import sample.LyricHandler as LyricHandler
import sample.ScreenHandler as ScreenHandler
import sample.config as config


def main():
    # Init wifi access point
    sh = SpotifyHandler.SpotifyHandler();
    lh = LyricHandler.LyricHandler();

    if len(sys.argv) > 1:
        try:
            print(f"Arguments passed: {sys.argv[1:]}")
            screenHandler = ScreenHandler.ScreenHandler(int(sys.argv[1]), int(sys.argv[2]));
        except ValueError:
            print("Invalid screen dimensions provided")
            return -1

    else:
        screenHandler = ScreenHandler.ScreenHandler();

    def checkSongAndAdjustLyric(isPlayingEvent: threading.Event):
        isPlayingEvent.wait()
        while True:
            trackStatus = sh.checkTrackStatus()
            lyric = lh.setCurrentTrack(sh.getCurrentTrack(),)
            screenHandler.updateScreen(trackStatus, lyric)
            if sh.isPlaying:
                time.sleep(config.CONST_DEFAULT_UPDATE_TRACK_FREQUENCY)
            else:
                isPlayingEvent.wait()


    isPlayingEvent = threading.Event()
    isPlayingEvent.clear()

    updateThread = threading.Thread(target=checkSongAndAdjustLyric, args=(isPlayingEvent,))
    updateThread.daemon = True
    updateThread.start()

    refreshTokenThread = threading.Thread(target=sh.refreshSpotify, args=(isPlayingEvent,))
    refreshTokenThread.daemon = True
    refreshTokenThread.start()

    checkIfPlayingThread = threading.Thread(target=sh.updateIsPlaying, args=(isPlayingEvent,))
    checkIfPlayingThread.daemon = True
    checkIfPlayingThread.start()

    screenHandler.startMainLoop()

    return 0

if __name__ == "__main__":
    main()