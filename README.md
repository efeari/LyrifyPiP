
# LyrifyPiP

A cross-platform desktop application that displays synchronized lyrics for currently playing music in a Picture-in-Picture (PiP) window. Supports both Windows Media Controls and Linux playerctl for system-wide music detection.

![image](https://github.com/user-attachments/assets/0421b284-25d0-47cf-ba07-07c94c464812)

![image](https://github.com/user-attachments/assets/ee54a3bf-fe0f-48ff-ba3e-54d0198a960e)

## How it works
### Media Detection System

* Prioritizes Spotify over other media players when multiple sources are playing
* Automatically detects song changes and playback status

#### Windows

* Uses Windows Media Control API to monitor system-wide media playback
* Tracks media session changes through events

#### Linux

* Integrates with playerctl for media control and metadata access
* Uses subprocess to monitor media players through playerctl commands
* Supports any MPRIS-compatible media player (Spotify, VLC, etc.)
* Continuously monitors playback status and metadata changes

### Callback Chain
#### Timeline Properties Changed Event
* Windows Media Control triggers events when media properties change
* Events include track changes, playback position updates, and metadata changes

#### Media Handler Callbacks
* Processes raw media events
* Extracts track information (title, artist, album art)
* Notifies the main application through registered callbacks
  
#### Lyric Handler Integration
* Receives track information from media callbacks
* Searches for matching lyrics using the syncedlyrics library
* Parses and synchronizes lyrics with playback position
  
### Visual Interface
* Implements a draggable Picture-in-Picture window
* Supports two background modes:
* Album artwork (with blur and transparency effects)
* Random color backgrounds
* Automatically adjusts text color for readability
* Shows/hides close button on hover
* Updates lyrics display in real-time

## Installation

## Usage
- Launch LyrifyPiP by running the application.
- The app will automatically detect the currently playing song and display its lyrics in a PiP window.

### Resources

* https://github.com/altdesktop/playerctl

### License
LyrifyPiP is open-source software licensed under the MIT License.
