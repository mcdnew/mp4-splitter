#!/usr/bin/env python3
"""
Split an MP4 into N chunks using FFmpeg stream copy (no re-encoding).
"""

import math
import shutil
import subprocess
import sys
from pathlib import Path

USAGE_TEXT = r"""
==============================================================
MP4 SPLITTER (FFmpeg - No Re-encoding, Lossless & Fast)
==============================================================

This script splits an .mp4 video into a number of equal chunks
using FFmpeg's stream copy mode (-c copy). This ensures:
  - No quality loss (original data preserved)
  - Much faster than re-encoding
  - Slightly approximate cut points (aligned to keyframes)

--------------------------------------------------------------
REQUIREMENTS:
--------------------------------------------------------------
1. FFmpeg & FFprobe must be installed and in your PATH.
   - Windows: Download from https://www.gyan.dev/ffmpeg/builds/
     Extract, add the 'bin' folder to PATH.
   - macOS: brew install ffmpeg
   - Linux (Debian/Ubuntu): sudo apt install ffmpeg
2. The input video must be an .mp4 file.
3. Python 3.8+ recommended.

--------------------------------------------------------------
USAGE EXAMPLES:
--------------------------------------------------------------
Interactive mode (will ask for file and chunk count):
    python split_mp4_ffmpeg.py

Direct mode (no prompts):
    python split_mp4_ffmpeg.py "/path/video.mp4" 4

Specify output directory:
    python split_mp4_ffmpeg.py "/path/video.mp4" 4 "/path/output"

--------------------------------------------------------------
OUTPUT:
--------------------------------------------------------------
Creates:
    video_part01.mp4, video_part02.mp4, ...
in the same folder as the original (or in the chosen output dir).

--------------------------------------------------------------
NOTE:
--------------------------------------------------------------
Because we're not re-encoding, cut points will be at keyframes.
This means chunk durations may vary slightly.
==============================================================
"""

def check_deps():
    """Ensure ffmpeg and ffprobe are available."""
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        print("ERROR: FFmpeg and FFprobe must be installed and on your PATH.")
        sys.exit(1)

def ffprobe_duration(path: Path) -> float:
    """Get video duration in seconds using ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True).strip()
    return float(out)

def split_video_stream_copy(file_path: Path, num_chunks: int, out_dir: Path | None = None):
    """Split MP4 into num_chunks using FFmpeg without re-encoding."""
    if num_chunks <= 0:
        raise ValueError("Number of chunks must be greater than zero.")
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    duration = ffprobe_duration(file_path)
    sec_per_chunk = duration / num_chunks

    base = file_path.stem
    out_dir = out_dir or file_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    # Zero-padded indices for tidy sorting: _part01, _part02, ...
    import math as _m
    digits = max(2, int(_m.ceil(_m.log10(num_chunks + 1))))
    template = f"{base}_part%0{digits}d.mp4"
    output_template = str(out_dir / template)

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-i", str(file_path),
        "-map", "0",
        "-c", "copy",
        "-f", "segment",
        "-segment_time", f"{sec_per_chunk:.6f}",
        "-reset_timestamps", "1",
        "-avoid_negative_ts", "make_zero",
        output_template,
    ]

    print(f"Duration: {duration:.2f} seconds")
    print(f"Target chunks: {num_chunks}")
    print(f"Approx seconds per chunk: {sec_per_chunk:.2f}")
    print(f"Output pattern: {output_template}")
    print("\nRunning FFmpeg...\n")

    proc = subprocess.Popen(cmd)
    proc.wait()

    if proc.returncode == 0:
        print("\n✅ Done! Files saved in:", out_dir)
    else:
        print("\n❌ FFmpeg encountered an error.")

if __name__ == "__main__":
    print(USAGE_TEXT)
    check_deps()

    args = sys.argv[1:]
    if len(args) >= 2:
        file_path = Path(args[0])
        num_chunks = int(args[1])
        out_dir = Path(args[2]) if len(args) >= 3 else None
    else:
        file_path = Path(input("Enter path to your .mp4 file: ").strip())
        num_chunks = int(input("Enter number of chunks: ").strip())
        out_dir_in = input("Output directory (leave blank for same folder): ").strip()
        out_dir = Path(out_dir_in) if out_dir_in else None

    split_video_stream_copy(file_path, num_chunks, out_dir)

