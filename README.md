# AlertCalifornia Tools

These tools are aimed to assist me with archiving data related to events in my
area from the CALFIRE & AlertCa wildfire monitoring system.

*Data is provided by <https://alertcalifornia.org/>.*

**If you use ANY of the
data provided by <https://alertcalifornia.com/>,
you must abide by *their*
Terms of Service: <https://alertcalifornia.org/faqs/>**

## Requirements

- Python 3
- `requests`
- `ffmpeg` is required to convert images to a time lapse video.

## Tools Included

### alertca_get_images.py

Example: `python alertca_get_images.py --outdir ~/Data/CALFIRE --feed-names Axis-MtnHighNorth1 Axis-MtnHighNorth2`

```shell
usage: alertca_get_images.py [-h] [--feed-names FEED_NAMES [FEED_NAMES ...]]

Grab images from a camera feed

options:
  -h, --help            show this help message and exit
  --feed-names FEED_NAMES [FEED_NAMES ...]
                        Name of the feed to grab
```

### generate_timelapse.py

Example: `python generate_timelapse.py --src-dir ~/Data/CALFIRE/camera_images  --outdir ~/Data/CALFIRE/video --overwrite`
