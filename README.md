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

## Example - scanning library
### Starting the scan
```
$ subsonic -c your_config.conf startScan
{
  "count": 18786,
  "scanning": true
}
```

### Checking Scan Status
```
$ subsonic -c your_config.conf getScanStatus
{
  "count": 18786,
  "scanning": false
}
```
