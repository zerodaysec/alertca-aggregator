"""alertca get images."""

import argparse
import os
from time import sleep
import random
import logging
import requests
from utils import get_random_user_agent, read_cameras_from_yaml
import concurrent.futures
from datetime import datetime
import json
from glob import glob

TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H%M%S")
TS_PFX = datetime.now().strftime("%Y-%m-%d_%H")


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

API_BASE = "https://cameras.alertcalifornia.org"
# WORKER_SLEEP = 60 * 60
SLOW_SLEEP = 0.5  # 1 for live
WORKERS = os.getenv("WORKERS", "2")
WORKERS = int(WORKERS)
logger.info("Starting up %s workers", WORKERS)
# sleep(5)

argparse = argparse.ArgumentParser(description="Grab images from a camera feed")
# argparse.add_argument(
#     "--fast-api",
#     help="Go fast mode...",
#     default=False,
#     action="store_true",
# )
argparse.add_argument(
    "--run-10s",
    help="Grap 10s feeds...",
    default=False,
    action="store_true",
)
argparse.add_argument(
    "--get-camdata",
    help="Get camdata json",
    default=False,
    action="store_true",
)
argparse.add_argument(
    "--run-1m",
    help="Grap 1m feeds...",
    default=False,
    action="store_true",
)
# argparse.add_argument(
#     "--shuffle",
#     help="Shuffle feeds list...",
#     default=False,
#     action="store_true",
# )
args = argparse.parse_args()

OUTPUT_DIR = "/data"
FEEDS = read_cameras_from_yaml()

# This is completely unnecessary but as I run a few copies in parallel
# this should make it so that we dont overlap on which cameras we are grabbing.
# if args.shuffle:
#     random.shuffle(FEEDS)


def get_feed_images_1min(feed_name):
    """get images for a given feed"""
    os.makedirs(f"{OUTPUT_DIR}/camera_images/{feed_name}", exist_ok=True)
    header = {"User-Agent": get_random_user_agent()}

    # https://cameras.alertcalifornia.org/public-camera-data/Axis-College1/1min/12-hour.json
    url = f"{API_BASE}/public-camera-data/{feed_name}/1min/12-hour.json"

    response = requests.get(url, headers=header, timeout=60).json()
    count = 0
    os.makedirs(f"{OUTPUT_DIR}/camera_images/{feed_name}", exist_ok=True)

    # get list in reverse as this allows us to target the oldest image first as
    # they drop off from the API first
    response["frames"].reverse()

    for frame in response["frames"]:
        filename = f"{OUTPUT_DIR}/camera_images/{feed_name}/1min_{frame}"

        if os.path.exists(filename):
            logger.debug("%s already exists!", filename)
            continue

        img_url = f"{API_BASE}/public-camera-data/{feed_name}/1min/{frame}"
        image = requests.get(img_url, headers=header, timeout=30)
        if image.status_code != 200:
            logger.warning("%s failed!", img_url)
            continue

        with open(filename, "wb") as file:
            file.write(image.content)
            logger.info("Wrote %s", filename)

        # if not args.fast_api:
        #     sleep(SLOW_SLEEP)

        count += 1


def get_feed_images_10sec(feed_name):
    """get images for a given feed"""
    os.makedirs(f"{OUTPUT_DIR}/camera_images/{feed_name}", exist_ok=True)
    header = {"User-Agent": get_random_user_agent()}

    url = f"{API_BASE}/public-camera-data/{feed_name}/10sec/30-min.json"
    response = requests.get(url, headers=header, timeout=60)
    if response.status_code != 200:
        logger.warning("%s failed!", url)
        logger.error("Response Code: %s", response.status_code)
        logger.error("Response: %s", response.text)
        return

    count = 0
    for frame in response.json()["frames"]:
        filename = f"{OUTPUT_DIR}/camera_images/{feed_name}/10sec_{frame}"

        if os.path.exists(filename):
            logger.debug("%s already exists!", filename)
            continue

        img_url = f"{API_BASE}/public-camera-data/{feed_name}/10sec/{frame}"
        image = requests.get(img_url, headers=header, timeout=30)
        if image.status_code != 200:
            logger.warning("%s failed!", img_url)
            continue

        with open(filename, "wb") as file:
            file.write(image.content)
            logger.info("Wrote %s", filename)

        # if not args.fast_api:
        #     sleep(SLOW_SLEEP)

        count += 1


def get_cam_data():
    url = "https://cameras.alertcalifornia.org/public-camera-data/all_cameras-v3.json"
    headers = {}
    resp = requests.get(url, timeout=30, headers=headers)
    if resp.status_code != 200:
        logger.error("Response Code: %s", resp.status_code)
        return
    else:
        outfile = f"{OUTPUT_DIR}/{TIMESTAMP}-cameras-v3.json"
        files = glob(f"{OUTPUT_DIR}/{TS_PFX}*-cameras-v3.json")
        if len(files) == 0:
            with open(outfile, "w") as file:
                json.dump(resp.json(), file)
        else:
            logger.info("Already downloaded %s", files)


def main():
    """main"""
    while True:
        WORKER_SLEEP = 60 * 30
        if args.get_camdata:
            get_cam_data()

        random.shuffle(FEEDS)
        if args.run_10s:
            batch_count = len(FEEDS)
            with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
                future_to_url = {
                    executor.submit(get_feed_images_1min, job["name"]): job
                    for job in FEEDS
                }
                for future in concurrent.futures.as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        data = future.result()
                        logger.debug(data)
                        batch_count -= 1
                        logger.warning(
                            "Jobs %s/%s left in get_feed_images_10s batch",
                            batch_count,
                            len(FEEDS),
                        )

                    except RuntimeWarning as exc:
                        logger.error("%r generated an exception: %s", url, exc)

        if args.run_1m:
            batch_count = len(FEEDS)
            with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as executor:
                future_to_url = {
                    executor.submit(get_feed_images_10sec, job["name"]): job
                    for job in FEEDS
                }
                for future in concurrent.futures.as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        data = future.result()
                        logger.debug(data)
                        batch_count -= 1
                        logger.warning(
                            "Jobs %s/%s left in get_feed_images_1m batch",
                            batch_count,
                            len(FEEDS),
                        )

                    except RuntimeWarning as exc:
                        logger.error("%r generated an exception: %s", url, exc)

        if args.run_10s:
            WORKER_SLEEP = 30

        if args.run_1m:
            # since these are 1min intervals, we dont need to run that frequently
            WORKER_SLEEP = 60 * 5

        logger.info("Poller runs done. Sleeping for %s", WORKER_SLEEP)
        sleep(WORKER_SLEEP)


if __name__ == "__main__":
    main()
