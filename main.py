import sys
import sample.SpotifyHandler as SpotifyHandler
import sample.LyricHandler as LyricHandler
import sample.ScreenHandler as ScreenHandler
import sample.config as config
import sample.OsMediaHandler as OsMediaHandler
import asyncio

async def main():
    # Init wifi access point
    #sh = SpotifyHandler.SpotifyHandler();
    lh = LyricHandler.LyricHandler()
    
    if len(sys.argv) > 1:
        try:
            print(f"Arguments passed: {sys.argv[1:]}")
            screenHandler = ScreenHandler.ScreenHandler(int(sys.argv[1]), int(sys.argv[2]), config.BackgroundChoice(sys.argv[3]));
        except ValueError:
            print("Invalid screen dimensions provided")
            return -1

    else:
        screenHandler = ScreenHandler.ScreenHandler();

    async def on_track_change(track):
        lyrics = lh.setCurrentTrack(track)
        currentState = config.TrackState.NOT_PLAYING
        if track == None:
            currentState = config.TrackState.NOT_PLAYING
        elif track and mh.isPlaying == False:
            currentState = config.TrackState.PAUSED_TRACK
        elif track and track != mh.getPreviousTrack():
            currentState = config.TrackState.NEW_TRACK
            mh.setPreviousTrack(mh.getCurrentTrack())
        elif track and track == mh.getPreviousTrack():
            currentState = config.TrackState.UPDATE_IN_PROGRESS

        screenHandler.updateScreen(currentState, lyrics)
        screenHandler.update()

    mh =  OsMediaHandler.OsMediaHandler(on_track_change_callback=on_track_change)

    try:
        await mh.start_monitoring()
    except KeyboardInterrupt:
        mh.stop_monitoring()

    # Start the main loop
    #screenHandler.startMainLoop()

    return 0

if __name__ == "__main__":
    asyncio.run(main())