"""Uses the SomaFM API and produces a .pls-format playlist with all the streams."""

# stdlib
import os
import time
import json
import errno
import hashlib
import StringIO
import tempfile
import ConfigParser

# Third party
import requests

def fetch(url, ttl = 1800, delay = 1.0):
    """Returns the content of the provided `url`, caching the results
    locally for `ttl` seconds."""
    cachepath = "%s/soma2pls_cache_%s" % (tempfile.gettempdir(),
        hashlib.md5(url).hexdigest())
    try:
        mtime = os.stat(cachepath).st_mtime
        
        assert mtime > (time.time() - ttl)

        return open(cachepath).read()
    except OSError, ex:
        if ex.errno != errno.ENOENT: # Does not exist.
            raise
    except AssertionError:
        pass # Cache file is too old.

    # Before making a HTTP request, wait a moment to try to be polite.
    time.sleep(delay)
    response = requests.get(url)
    open(cachepath, "w").write(response.content)
    return response.content

def parsepls(pls):
    """A generator that parses a .pls playlist and produces dicts of the
    form:
    {'title': ..., 'url': ...}"""
    playlist = ConfigParser.ConfigParser()
    playlist.readfp(StringIO.StringIO(pls))
    for index in xrange(1, playlist.getint("playlist", "numberofentries") + 1):
        yield {'url': playlist.get("playlist", "File%d" % index),
            'title': playlist.get("playlist", "Title%d" % index)}

def getStations(args):
    """A generator that fetches stream metadata from SomaFM's API and
    produces dicts of the form:
    {'stream_url': ..., 'title': ..., 'logo': ..., 'descr': ...}"""
    
    channels = json.loads(fetch(args.url, delay=args.fetch_delay))
 
    for channel in channels['channels']:
        # By SomaFM convention, the highest quality streams are found
        # in the first playlist.
        pls_url = channel['playlists'][0]['url']
        pls_content = fetch(pls_url, delay=args.fetch_delay)
        streams = parsepls(pls_content)
        
        for stream in streams:
            yield {'stream_url': stream['url'], 'title': channel['title'],
                'logo': channel['image'], 'descr': channel['description']}
 
            if args.one_stream:
                break

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", action="store",
        default="http://api.somafm.com/channels.json")
    parser.add_argument("--one-stream", action="store_true", default=False,
        help="Uses the first stream URL found for each station.")
    parser.add_argument("--fetch-delay", type=int, action="store",
        default=1, help="Seconds to wait between HTTP requests")
    args = parser.parse_args()
    
    print "[playlist]"
    stations = list(getStations(args))
    
    print "numberofentries=%d" % len(stations)
 
    stations.sort(key = lambda station: station['title'])
 
    for index, station in enumerate(stations):
        print "File%d=%s"    % (index, station['stream_url'])
        print "Title%d=%s - %s"   % (index, station['title'],
            station['descr'])
        print "Length%d=-1"  % (index, )


