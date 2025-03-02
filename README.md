
# LyrifyPiP

LyrifyPiP is a desktop application that enhances your music listening experience by displaying lyrics of the currently playing song in a Picture-in-Picture (PiP) window. It is designed to work with various music sources and platforms, allowing you to view lyrics seamlessly while multitasking.

![image](https://github.com/user-attachments/assets/0421b284-25d0-47cf-ba07-07c94c464812)

![image](https://github.com/user-attachments/assets/ee54a3bf-fe0f-48ff-ba3e-54d0198a960e)

## How it works
### Media Detection System

* Uses Windows Media Control API to monitor system-wide media playback
* Prioritizes Spotify over other media players when multiple sources are playing
* Tracks media session changes through an event-based system
* Automatically detects song changes and playback status

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

### License
LyrifyPiP is open-source software licensed under the MIT License.
