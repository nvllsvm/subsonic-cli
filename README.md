# subsonic-cli

A command line tool for the Subsonic HTTP API.

## Installation
```
pip install subsonic-cli
```

## Configuration
```
[subsonic-cli]
url = https://airsonic.yourdomain.com
username = YOUR_USER
password = YOUR_PASSWORD
```

## Examples

### Library Scanning
```
$ subsonic-cli -c your_config.conf startScan
{
  "count": 18786,
  "scanning": true
}
```

### Retrieving Top Songs
```
$ subsonic-cli -c config.cfg getTopSongs -p artist Autodafeh
{
  "song": [
    {
      "album": "Act Of Faith",
      "albumId": "1760",
      "artist": "Autodafeh",
      "artistId": "345",
      "bitRate": 243,
      "contentType": "audio/mpeg",
      "coverArt": "34871",
      "created": "2018-07-19T00:06:01.000Z",
      "duration": 217,
      "genre": "EBM",
      "id": "34960",
      "isDir": false,
      "isVideo": false,
      "parent": "34871",
      "path": "Autodafeh/Autodafeh - Act Of Faith (2011) FLAC/06 - Watch Out.mp3",
      "playCount": 83,
      "size": 6638974,
      "suffix": "mp3",
      "title": "Watch Out",
      "track": 6,
      "type": "music",
      "year": 2011
    }
  ]
}
```

### Streaming Music to MPV
The `id` parameter value was retrieved in the *Retrieving Top Songs* example.
```
$ subsonic-cli -c config.cfg stream -p id 34960 | mpv -
```
