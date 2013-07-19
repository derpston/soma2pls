soma2pls
========

Scrapes somafm.com and generates a .pls-format playlist with all the stream URLs.

Features
--------

* Is relatively polite to somafm.com.
 * Caches intermediate data in /tmp/
 * Waits 1 second between HTTP requests.
 * ... though it's not _that_ polite because it ignores robots.txt
* All streams for each station are produced.
* Streams are sorted by their titles.

Dependencies
------------

* requests
* BeautifulSoup

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

