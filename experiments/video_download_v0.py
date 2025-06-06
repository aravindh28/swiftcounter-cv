import argparse
import os
import yt_dlp


def download_video(url, filename):
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        print(
            f"✅ File '{filename}' already exists and is non-empty. Skipping download."
        )
        return

    ydl_opts = {
        "outtmpl": filename,
        "format": "best[ext=mp4]/best",
        "quiet": False,
        "noplaylist": True,
    }

    # Use cookies if found in data/
    cookies_path = os.path.join("data", "cookies.txt")
    if os.path.exists(cookies_path):
        print(f"🔐 Using cookies from '{cookies_path}'")
        ydl_opts["cookies"] = cookies_path

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print(f"📥 Downloading video from {url} to {filename}")
        try:
            ydl.download([url])
            print("✅ Download complete!")
        except Exception as e:
            print(f"❌ Download failed:\n{e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download a YouTube video using yt-dlp (with optional cookies.txt)"
    )
    parser.add_argument("--video-url", required=True, help="YouTube video URL")
    parser.add_argument(
        "--filename", default="data/downloaded_video.mp4", help="Output filename"
    )
    args = parser.parse_args()

    download_video(args.video_url, args.filename)
