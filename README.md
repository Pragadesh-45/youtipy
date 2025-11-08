# youtipy

**version 0.2**

a simple command-line yt music player that searches for songs and plays them using `yt-dlp` and `mpv`. supports both single songs and youtube playlists with full navigation controls.

## need

wanted a simple ad-less, distraction-less music player from youtube which can be accessed from terminal.

## prerequisites

before using youtipy, you need to install the following external tools:

### macos (using homebrew)

```bash
brew install mpv
```

**note**: `yt-dlp` will be installed automatically via pip in the virtual environment setup.

## installation

### 1. clone the repository

```bash
git clone https://github.com/Pragadesh-45/youtipy.git
cd youtipy
```

### 2. set up python virtual environment

```bash
# create virtual environment
python3 -m venv venv

# activate virtual environment
source venv/bin/activate

# install python dependencies
pip install -r requirements.txt
```

### 3. verify installation

* ensure python 3.6+ is installed
* the `cookies.txt` file should be present for youtube access (needed for age-restricted videos)
* test that both `yt-dlp` and `mpv` work:

```bash
yt-dlp --version
mpv --version
```

## cookies setup (optional)

youtipy requires a `cookies.txt` file to handle login-based or age-restricted youtube content.
you can easily generate this using the **cookies.txt browser extension**:

1. install the extension for your browser:

   * [Get cookies.txt LOCALLY for chrome](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   * [cookies.txt for firefox](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)
2. log in to youtube in your browser.
3. click on the extension and export cookies for `youtube.com`.
4. save the file as `cookies.txt` inside your `youtipy` folder.

## usage

### first, activate your virtual environment

```bash
source venv/bin/activate
```

### basic usage

```bash
# play a single song
python3 youtipy.py "song name"

# play a youtube playlist
python3 youtipy.py "https://www.youtube.com/playlist?list=PLxxxxx"
```

### interactive mode

```bash
python3 youtipy.py
# you'll be prompted to enter a song name or playlist URL
```

### with loop count

```bash
# play song 3 times
python3 youtipy.py "song name" 3

# infinite loop (default)
python3 youtipy.py "song name" -1

# loop playlist 2 times
python3 youtipy.py "https://www.youtube.com/playlist?list=PLxxxxx" 2
```

### playlist navigation

when playing a playlist, you can navigate using mpv's built-in controls:

- `>` or `]` - next track
- `<` or `[` - previous track
- `SPACE` - pause/resume
- `q` - quit
- `LEFT` - seek backward 10s
- `RIGHT` - seek forward 10s
- `UP` - volume up
- `DOWN` - volume down

### set up an alias for easier access (recommended)

add this to your shell configuration file (`~/.zshrc` or `~/.bashrc`):

```bash
alias youtipy='cd /path/to/youtipy && source venv/bin/activate && python3 youtipy.py'
```

replace `/path/to/youtipy` with the actual path to your youtipy directory.

after adding the alias, reload your shell configuration:

```bash
source ~/.zshrc    # for zsh
# or
source ~/.bashrc   # for bash
```

### make it executable (alternative approach)

```bash
chmod +x youtipy.py
./youtipy.py "song name"
```

## examples

### single songs

```bash
# play "thuli thuli" once
python3 youtipy.py "thuli thuli"

# play "boomi enna suththuthe" 5 times
python3 youtipy.py "boomi enna suththuthe" 5

# play "wide putin walk" infinitely
python3 youtipy.py "wide putin walk" -1
```

### playlists

```bash
# play a playlist (infinite loop)
python3 youtipy.py "https://www.youtube.com/playlist?list=PLxxxxx" -1

# play a playlist 2 times
python3 youtipy.py "https://www.youtube.com/playlist?list=PLxxxxx" 2

# play from a video URL that's part of a playlist
python3 youtipy.py "https://www.youtube.com/watch?v=xxxxx&list=PLxxxxx"
```

### interactive mode

```bash
python3 youtipy.py
```

## using the alias (example)
```bash
╰─ youtipy "thuli thuli" -1                                                             ─╯
● audio  --aid=1  --alang=eng  (opus 2ch 48000 hz) [default]
ao: [coreaudio] 48000hz stereo 2ch floatp
a: 00:04:01 / 00:04:48 (84%) cache: 46s/1mb

```

## how it works

### single songs

1. **search**: the script uses `yt-dlp` to search youtube for your query + "lyrical video".
2. **extract**: it gets the best audio-only stream url from the first search result.
3. **play**: it uses `mpv` to play the audio stream without video.

### playlists

1. **detect**: automatically detects if the input is a playlist URL (or video URL with playlist parameter).
2. **extract**: fetches all video IDs from the playlist using `yt-dlp`.
3. **process**: gets the best audio stream URL for each video in the playlist.
4. **play**: uses `mpv`'s native playlist support to play all tracks with full navigation controls.

## features

- ✅ single song playback with search
- ✅ youtube playlist support with navigation
- ✅ keyboard controls for playlist navigation
- ✅ automatic playlist detection from video URLs
- ✅ loop support for both songs and playlists
- ✅ skips unavailable videos in playlists gracefully

## possible future enhancements
- [ ] queue support (with navigation support)
- [ ] loop a song within a certain interval (for audio jukeboxes and OSTs)

## configuration

* **cookie file**: `cookies.txt` contains youtube cookies for better access.
* **audio format**: automatically selects best available audio quality.
* **loop behavior**: default is infinite loop (-1), can be customized.

## dependencies

* python3
* yt-dlp (installed via pip)
* mpv (system installation required)

## demo
https://github.com/user-attachments/assets/567eae7a-e29b-4fdf-acf5-46e314273e3e

## license

this project's license is under MIT.

## contributing

feel free to report issues or submit pull requests to improve the project.
