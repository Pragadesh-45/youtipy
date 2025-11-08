#!/usr/bin/env python3

import subprocess
import threading
import sys
import urllib.parse
import re

COOKIE_FILE = "cookies.txt"

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
                "--quiet",
                "--cookies", COOKIE_FILE
            ],
            text=True,
            stderr=subprocess.DEVNULL
        ).strip()
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
                "--cookies", COOKIE_FILE
            ],
            text=True,
            stderr=subprocess.DEVNULL
        ).strip().split('\n')
        video_ids = [vid.strip() for vid in video_ids if vid.strip()]

        # Then get the stream URL for each video
        urls = []
        total = len(video_ids)
        for idx, vid_id in enumerate(video_ids, 1):
            try:
                result = subprocess.run(
                    [
                        "yt-dlp",
                        "-f", "bestaudio",
                        "--get-url",
                        "--quiet",
                        f"https://www.youtube.com/watch?v={vid_id}",
                        "--cookies", COOKIE_FILE
                    ],
                    text=True,
                    capture_output=True,
                    check=True
                )
                url = result.stdout.strip()
                if url:
                    urls.append(url)
                    print(f"✓ [{idx}/{total}] Video {vid_id} ready", end='\r')
            except subprocess.CalledProcessError as e:
                # Try to extract error message from stderr
                error_msg = e.stderr.strip() if e.stderr else "Unknown error"
                if "unavailable" in error_msg.lower() or "private" in error_msg.lower() or "deleted" in error_msg.lower():
                    reason = "unavailable"
                elif "age-restricted" in error_msg.lower():
                    reason = "age-restricted"
                else:
                    reason = "failed to extract"
                print(f"✗ [{idx}/{total}] Video {vid_id} - {reason}, skipping...")
                continue

        if urls:
            print(f"\n✓ Successfully loaded {len(urls)}/{total} videos")

        return urls
    except subprocess.CalledProcessError:
        print("Failed to fetch playlist URLs. Check yt-dlp installation and cookies.")
        return []

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

    # Use mpv's native playlist support for navigation
    mpv_args = ["mpv", "--no-video"]

    if loop == -1:
        mpv_args.append("--loop-playlist=inf")
    elif loop > 0:
        mpv_args.append(f"--loop-playlist={loop}")

    # Add all URLs to mpv command
    mpv_args.extend(urls)

    subprocess.run(mpv_args)

def play_song(query, loop=-1):
    # Hybrid approach: fetch URL in a background thread and start playback.
    url_thread = threading.Thread(target=lambda: play_url(get_first_url(query), loop))
    url_thread.start()
    url_thread.join()

if __name__ == "__main__":
    # Command-line song input
    song = sys.argv[1] if len(sys.argv) > 1 else input("Enter song name or playlist URL: ")

    # Clean the URL to handle shell escaping
    song = clean_url(song)

    # Optional: loop count as second argument
    loop = int(sys.argv[2]) if len(sys.argv) > 2 else -1

    # Check if input is a playlist URL
    if is_playlist_url(song) or song.startswith("http"):
        play_playlist(song, loop=loop)
    else:
        # Only lyrical songs for now
        song += " lyrical video"
        play_song(song, loop=loop)
