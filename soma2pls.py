""" Scrapes somafm.com and produces a .pls-format playlist with all the streams."""

# stdlib
import re
import os
import time
import errno
import hashlib
import StringIO
import tempfile
import ConfigParser

# Third party
import requests
import BeautifulSoup

def fetch(url, ttl = 1800, delay = 1.0):
   """Returns the content of the provided `url`, caching the results locally for `ttl` seconds."""
   cachepath = "%s/soma2pls_cache_%s" % (tempfile.gettempdir(), hashlib.md5(url).hexdigest())
   try:
      mtime = os.stat(cachepath).st_mtime
      
      assert mtime > (time.time() - ttl)

      return open(cachepath).read()
   except OSError, ex:
      if ex.errno != errno.ENOENT: # Does not exist.
         raise
   except AssertionError:
      pass # Cache file is too old.

   # Before making a HTTP request, wait a moment to try to be polite to the scraped site.
   time.sleep(delay)
   response = requests.get(url)
   open(cachepath, "w").write(response.content)
   return response.content

def parsepls(pls):
   """A generator that parses a .pls playlist and produces {'title': ..., 'url': ...} dicts."""
   playlist = ConfigParser.ConfigParser()
   playlist.readfp(StringIO.StringIO(pls))
   for index in xrange(1, playlist.getint("playlist", "numberofentries") + 1):
      yield {'url': playlist.get("playlist", "File%d" % index), 'title': playlist.get("playlist", "Title%d" % index)}

def getStations():
   """A generator that scrapes somafm.com and produces {'streams': ..., 'name': ..., 'logo': ..., 'descr': ...} dicts."""
   baseurl = "http://www.somafm.com%s"
   
   listenpage = fetch(baseurl % "/listen/")
   listensoup = BeautifulSoup.BeautifulSoup(listenpage)

   for header in listensoup.findAll("h3"):
      descr = header.findNext("p", "descr")
      logo = header.findPrevious("img")
      mp3_links = header.findNext("span", text = re.compile("^MP3:"))
      path = mp3_links.findNextSibling("a")["href"]
   
      stationpage = fetch(baseurl % path)
   
      if "[playlist]" in stationpage:
         # Oops, this is a .pls file, not a station detail page.
         streams = parsepls(stationpage)
      else:
         stationsoup = BeautifulSoup.BeautifulSoup(stationpage)
         pls_path = stationsoup.findAll("a", text = re.compile("Start stream in external player"))[0].findParent()['href']
         pls = fetch(baseurl % pls_path)
         streams = parsepls(pls)
   
      yield {'streams': streams, 'name': header.text, 'logo': baseurl % logo['src'], 'descr': descr.text}

if __name__ == "__main__":
   # Generates a .pls-format playlist.

   print "[playlist]"
   stations = getStations()
   streams = []

   for station in stations:
      for stream in station['streams']:
         streams.append(stream)
   
   print "numberofentries=%d" % len(streams)

   streams.sort(key = lambda stream: stream['title'])

   for index, stream in enumerate(streams):
      print "File%d=%s"    % (index, stream['url'])
      print "Title%d=%s"   % (index, stream['title'])
      print "Length%d=-1"  % (index, )


