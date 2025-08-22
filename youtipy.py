#!/usr/bin/env python3

import subprocess
import threading
import sys

COOKIE_FILE = "cookies.txt"

def get_first_url(query):
    # Fetch the first playable YouTube URL using yt-dlp and cookies.
    try:
        url = subprocess.check_output(
            [
                "yt-dlp",
                "-f", "bestaudio",
                "--no-playlist",
                f"ytsearch1:{query}",
                "--get-url",
                "--cookies", COOKIE_FILE
            ],
            text=True
        ).strip()
        return url
    except subprocess.CalledProcessError:
        print("Failed to fetch URL. Check yt-dlp installation and cookies.")
        return None

def play_url(url, loop=-1):
    # Play a YouTube URL in mpv.
    # loop=-1 -> infinite loop, loop=N -> play N times
    if url:
        if loop == -1:
            subprocess.run(["mpv", "--no-video", "--loop", url])
        else:
            subprocess.run(["mpv", "--no-video", f"--loop={loop}", url])
    else:
            print("No URL to play.")

def play_song(query, loop=-1):
    # Hybrid approach: fetch URL in a background thread and start playback.
    url_thread = threading.Thread(target=lambda: play_url(get_first_url(query), loop))
    url_thread.start()
    url_thread.join()

if __name__ == "__main__":
    # Command-line song input
    song = sys.argv[1] if len(sys.argv) > 1 else input("Enter song name: ")

    # Only lyrical songs for now
    song += " lyrical video"

    # Optional: loop count as second argument
    loop = int(sys.argv[2]) if len(sys.argv) > 2 else -1

    play_song(song, loop=loop)
