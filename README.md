soma2pls
========

Generates a .pls-format playlist with all the SomaFM streams.

Features
--------

* Is relatively polite to somafm.com.
 * Caches intermediate data in /tmp/
 * Waits 1 second between HTTP requests.
 * ... though it's not _that_ polite because it ignores robots.txt
* All streams for each station are produced.
 * Use --one-stream to use just the first stream.
* Streams are sorted by their titles.

Usage
-----

```shell
$ python soma2pls.py --help
usage: soma2pls.py [-h] [--url URL] [--one-stream] [--fetch-delay FETCH_DELAY]

optional arguments:
  -h, --help            show this help message and exit
  --url URL
  --one-stream          Uses the first stream URL found for each station.
  --fetch-delay FETCH_DELAY
                        Seconds to wait between HTTP requests
```

Dependencies
------------

* requests

Example
-------
```bash
$ python soma2pls.py
[playlist]
numberofentries=64
File0=http://mp4.somafm.com:8080
Title0=SomaFM: BAGeL Radio (#1 128 mp3): What alternative rock radio should sound like.
Length0=-1
...
```

