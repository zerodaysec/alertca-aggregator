"""generate timelapse"""

import argparse
import logging
import os
import subprocess
from glob import glob

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")

argparse = argparse.ArgumentParser(description="Grab images from a camera feed")
argparse.add_argument(
    "--overwrite",
    help="Overwrite existing videos (Default: False)",
    action="store_true",
    default=False,
)
argparse.add_argument(
    "--src-dir",
    help="Name of the feed to grab",
    type=str,
    required=True,
)
argparse.add_argument(
    "--outdir", help="Name of the feed to grab", type=str, required=True
)

args = argparse.parse_args()

BASE_DIR = args.src_dir
DIRS = os.listdir(BASE_DIR)


def main():
    """main"""
    if not os.path.exists(args.outdir):
        os.mkdir(args.outdir)

    for d in DIRS:
        if d == ".DS_Store":
            continue

        glob_str = f"{BASE_DIR}/{d}/10sec_*.jpg"
        if len(glob(glob_str)) > 0:
            outfle = f"{args.outdir}/{d}_10sec.mp4".replace("Axis-", "")
            if os.path.exists(outfle) and args.overwrite is False:
                logger.warning("File %s exists and no --overwrite supplied", outfle)
                continue
            try:
                subprocess.run(
                    [
                        "ffmpeg",
                        "-framerate",
                        "12",
                        "-pattern_type",
                        "glob",
                        "-i",
                        glob_str,
                        "-c:v",
                        "libx264",
                        outfle,
                        "-y",
                    ],
                    check=True,
                    # stderr=subprocess.PIPE,
                    # stdout=subprocess.PIPE,
                )
            except subprocess.CalledProcessError as e:
                logger.error(e)

        glob_str = f"{BASE_DIR}/{d}/1min_*.jpg"
        if len(glob(glob_str)) > 0:
            outfle = f"{args.outdir}/{d}_1min.mp4".replace("Axis-", "")
            if os.path.exists(outfle) and args.overwrite is False:
                logger.warning("File %s exists AND --overwrite not supplied", outfle)
                continue
            try:
                subprocess.run(
                    [
                        "ffmpeg",
                        "-framerate",
                        "6",
                        "-pattern_type",
                        "glob",
                        "-i",
                        glob_str,
                        "-c:v",
                        "libx264",
                        outfle,
                        "-y",
                    ],
                    check=True,
                    # stderr=subprocess.PIPE,
                    # stdout=subprocess.PIPE,
                )
                logger.info("Generated %s", f"{args.outdir}/{d}_1min.mp4")
            except subprocess.CalledProcessError as e:
                logger.error(e)


if __name__ == "__main__":
    main()
