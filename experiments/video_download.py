"""import argparse
import os
import yt_dlp

def download_video(url, filename, start=None, end=None):
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        print(
            f"✅ File '{filename}' already exists and is non-empty. Skipping download."
        )
        return
    

    ydl_opts = {
        "outtmpl": filename,
        "format": "bestvideo[height<=720][ext=mp4]/bestvideo[height<=720]/best",
        "merge_output_format": "mp4",
        "quiet": False,
        "noplaylist": True,
    }

    # If both start and end are provided, add download_sections
    if start is not None and end is not None:
        ydl_opts["download_sections"] = f"*{start}-{end}"

    # Use cookies if found in data/
    cookies_path = os.path.join("data", "cookies.txt")
    if os.path.exists(cookies_path):
        print(f"🔐 Using cookies from '{cookies_path}'")
        ydl_opts["cookies"] = cookies_path

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"📥 Downloading video from {url} to {filename}")
        if start is not None and end is not None:
            print(f"⏱️ Downloading from {start} to {end} seconds")
        try:
            ydl.download([url])
            print("✅ Download complete!")
        except Exception as e:
            print(f"❌ Download failed:\n{e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download a YouTube video (optionally a segment) using yt-dlp (with optional cookies.txt)"
    )
    parser.add_argument("--video-url", required=True, help="YouTube video URL")
    parser.add_argument(
        "--start", type=int, default=None, help="Start time in seconds (optional)"
    )
    parser.add_argument(
        "--end", type=int, default=None, help="End time in seconds (optional)"
    )
    parser.add_argument(
        "--filename",
        default=os.path.join("data", "downloaded_video.mp4"),
        help="Output filename (default: data/downloaded_video.mp4)"
    )

    args = parser.parse_args()

    # Ensure the parent directory exists
    parent = os.path.dirname(args.filename)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)

    download_video(args.video_url, args.filename, args.start, args.end)
"""

import argparse
import os
import yt_dlp
import subprocess


def download_video(url, filename, start=None, end=None):
    # Download to a temporary file if segmenting
    if start is None and end is None:
        temp_filename = filename.replace(".mp4", "_raw.mp4")
    else:
        print(f"Downloading segment from {start} to {end}")
        temp_filename = filename
        # Create a filename with start and/or end times
        base, ext = os.path.splitext(filename)
        suffix = ""
        if start is not None:
            suffix += f"_start{start}"
        if end is not None:
            suffix += f"_end{end}"
        filename = f"{base}{suffix}{ext}"
        temp_filename = filename

    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        print(
            f"✅ File '{filename}' already exists and is non-empty. Skipping download."
        )
        return

    ydl_opts = {
        "outtmpl": temp_filename,
        "format": "bestvideo[height<=720][ext=mp4]/bestvideo[height<=720]/best",
        "merge_output_format": "mp4",
        "quiet": False,
        "noplaylist": True,
    }

    # Use cookies if found in data/
    cookies_path = os.path.join("data", "cookies.txt")
    if os.path.exists(cookies_path):
        print(f"🔐 Using cookies from '{cookies_path}'")
        ydl_opts["cookies"] = cookies_path

    print(f"📥 Downloading video from {url} to {temp_filename}")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            print("✅ Download complete!")
        except Exception as e:
            print(f"❌ Download failed:\n{e}")
            return

    # If segment requested, trim with ffmpeg for frame accuracy
    if start is not None and end is not None:
        precise_trim(temp_filename, filename, start, end)
        if temp_filename != filename:
            os.remove(temp_filename)


def precise_trim(input_path, output_path, start, end):
    duration = end - start
    print(f"✂️  Trimming {input_path} from {start}s to {end}s into {output_path}")
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-ss",
        str(start),
        "-t",
        str(duration),
        "-c:v",
        "libx264",
        "-an",  # no audio
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode == 0:
        print("✅ Precise trim complete!")
    else:
        print(f"❌ ffmpeg trimming failed:\n{result.stderr.decode()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download a YouTube video (optionally a segment, frame-accurate) using yt-dlp."
    )
    parser.add_argument("--video-url", required=True, help="YouTube video URL")
    parser.add_argument(
        "--start", type=int, default=None, help="Start time in seconds (optional)"
    )
    parser.add_argument(
        "--end", type=int, default=None, help="End time in seconds (optional)"
    )
    parser.add_argument(
        "--filename",
        default=os.path.join("data", "downloaded_video.mp4"),
        help="Output filename (default: data/downloaded_video.mp4)",
    )

    args = parser.parse_args()

    # Ensure the parent directory exists
    parent = os.path.dirname(args.filename)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)

    download_video(args.video_url, args.filename, args.start, args.end)
