def formatMilliSecond(timeMS):
    minute = timeMS / 60000
    second = timeMS - minute * 60
    milliSecond = timeMS - (minute * 60000 + second * 1000)

    return minute, second, milliSecond

def reformatToMilliSecond(minute, seconds, milliSecond):
    return (minute * 60000 + seconds * 1000 + milliSecond)