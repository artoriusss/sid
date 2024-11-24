# SID: Satelite Imagery Downloader

A toolkit for downloading satelite imagery from Google API. 

## Installation:

```
pip install pysatimage
```

## Working example:
To utilize the library, import `fetch_image` function and input geographic coordinates like in the following code snippet:

```
from SID import fetch_image

fetch_image(-3.13028, -59.87657)
```

Within the very first run, you'll be asked to configure three parameters:
- Zoom level
- Image resolution (desired image width and height)

If you ever need to change these, you can do so in `.config/sid_preferences.json`.

After running the code, you can view your image(s) in `sid_images/`, which will be located in the root of your project.

![example1](images/example1.png)
![example2](images/example2.png)