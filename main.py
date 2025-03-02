import asyncio
import sys
import sample.LyrifyPiP as LyrifyPiP

async def main():
    LyrifyPiP_app = LyrifyPiP.LyrifyPiP(sys.argv)
    await LyrifyPiP_app.run()
    return 0

if __name__ == "__main__":
    asyncio.run(main())