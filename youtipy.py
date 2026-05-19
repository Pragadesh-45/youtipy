#!/usr/bin/env python3

import subprocess
import sys
import os
import urllib.parse
import re
import socket
import json

__version__ = "0.3.1"

COOKIE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cookies.txt")
SOCKET_PATH = "/tmp/youtipy.sock"

def clean_url(url):
    # Remove shell escaping and clean up the URL
    # Remove backslashes that might have been added by shell escaping
    url = url.replace('\\', '')
    # Decode any URL encoding
    try:
        url = urllib.parse.unquote(url)
    except:
        pass
    return url.strip()

def extract_playlist_id(url):
    # Extract playlist ID from URL (handles both playlist URLs and video URLs with list parameter)
    url = clean_url(url)
    # Try to extract list parameter
    match = re.search(r'[?&]list=([^&]+)', url)
    if match:
        return match.group(1)
    return None

def is_playlist_url(url):
    # Check if the URL is a YouTube playlist URL
    url = clean_url(url)
    return "playlist" in url.lower() or "list=" in url.lower()

def get_first_watch_url(query):
    # Fetch the YouTube watch URL (not stream URL) to avoid expiry issues.
    try:
        url = subprocess.check_output(
            [
                "yt-dlp",
                "--flat-playlist",
                f"ytsearch1:{query}",
                "--print", "webpage_url",
                "--quiet",
                "--cookies", COOKIE_FILE,
            ],
            text=True,
            stderr=subprocess.DEVNULL
        ).strip().splitlines()[0]
        return url
    except subprocess.CalledProcessError:
        print("Failed to fetch URL. Check yt-dlp installation and cookies.")
        return None

def get_playlist_urls(playlist_url):
    # Fetch all video stream URLs from a YouTube playlist
    try:
        playlist_url = clean_url(playlist_url)

        # Extract playlist ID if it's a video URL with list parameter
        playlist_id = extract_playlist_id(playlist_url)
        if playlist_id:
            # Use the playlist ID directly for better reliability
            playlist_url = f"https://www.youtube.com/playlist?list={playlist_id}"

        # First, get all video IDs from the playlist
        video_ids = subprocess.check_output(
            [
                "yt-dlp",
                "--flat-playlist",
                "--print", "%(id)s",
                "--quiet",
                playlist_url,
                "--cookies", COOKIE_FILE,
                "--extractor-args", EXTRACTOR_ARGS,
            ],
            text=True,
            stderr=subprocess.DEVNULL
        ).strip().split('\n')
        video_ids = [vid.strip() for vid in video_ids if vid.strip()]

        # Build watch URLs directly — let mpv/yt-dlp resolve streams at play time
        urls = [f"https://www.youtube.com/watch?v={vid_id}" for vid_id in video_ids]
        print(f"✓ Loaded {len(urls)} videos from playlist")
        return urls
    except subprocess.CalledProcessError:
        print("Failed to fetch playlist URLs. Check yt-dlp installation and cookies.")
        return []

EXTRACTOR_ARGS = "youtube:player_client=android_vr"

def mpv_ytdl_args():
    return [
        f"--ytdl-raw-options=cookies={COOKIE_FILE},extractor-args={EXTRACTOR_ARGS}",
        f"--input-ipc-server={SOCKET_PATH}",
    ]

def ipc_command(cmd):
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
            s.connect(SOCKET_PATH)
            s.sendall((json.dumps({"command": cmd}) + "\n").encode())
            s.recv(4096)  # wait for mpv's response before closing
    except FileNotFoundError:
        print("No active youtipy session. Start one first.")
        sys.exit(1)
    except ConnectionRefusedError:
        print("youtipy session not responding.")
        sys.exit(1)

def enqueue(query):
    query = clean_url(query)
    if is_playlist_url(query) or query.startswith("http"):
        urls = get_playlist_urls(query)
        for url in urls:
            ipc_command(["loadfile", url, "append-play"])
        msg = f"Queued {len(urls)} videos from playlist."
        ipc_command(["show-text", f"⏭ {msg}", "3000"])
        print(msg)
    else:
        display_name = query
        query += " lyrical video"
        url = get_first_watch_url(query)
        if url:
            ipc_command(["loadfile", url, "append-play"])
            ipc_command(["show-text", f"⏭ Queued: {display_name}", "3000"])
            print(f"Queued: {display_name}")

def play_url(url, loop=-1):
    if not url:
        print("No URL to play.")
        return
    args = ["mpv", "--no-video"] + mpv_ytdl_args()
    args.append("--loop-playlist=inf" if loop == -1 else f"--loop-playlist={loop}")
    args.append(url)
    subprocess.run(args)

def play_playlist(playlist_url, loop=-1):
    # Play all videos in a playlist with navigation support
    urls = get_playlist_urls(playlist_url)
    if not urls:
        print("No videos found in playlist.")
        return

    print(f"Found {len(urls)} videos in playlist. Starting playback...")
    print("\n" + "="*50)
    print("Playlist Navigation Controls:")
    print("  > or ]  - Next track")
    print("  < or [  - Previous track")
    print("  SPACE   - Pause/Resume")
    print("  q       - Quit")
    print("  LEFT    - Seek backward 10s")
    print("  RIGHT   - Seek forward 10s")
    print("  UP      - Volume up")
    print("  DOWN    - Volume down")
    print("="*50 + "\n")

    mpv_args = ["mpv", "--no-video"] + mpv_ytdl_args()

    if loop == -1:
        mpv_args.append("--loop-playlist=inf")
    elif loop > 0:
        mpv_args.append(f"--loop-playlist={loop}")

    mpv_args.extend(urls)
    subprocess.run(mpv_args)

def play_song(query, loop=-1):
    url = get_first_watch_url(query)
    play_url(url, loop)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--version", "-v"):
        print(f"youtipy v{__version__}")
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] == "skip":
        ipc_command(["playlist-next", "force"])
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1] == "enqueue":
        if len(sys.argv) < 3:
            print("Usage: youtipy enqueue <song name or URL>")
            sys.exit(1)
        enqueue(sys.argv[2])
        sys.exit(0)

    song = sys.argv[1] if len(sys.argv) > 1 else input("Enter song name or playlist URL: ")
    song = clean_url(song)
    loop = int(sys.argv[2]) if len(sys.argv) > 2 else -1

    if is_playlist_url(song) or song.startswith("http"):
        play_playlist(song, loop=loop)
    else:
        song += " lyrical video"
        play_song(song, loop=loop)
