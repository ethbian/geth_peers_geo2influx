#!/usr/bin/env python
"""
v0.2
Use the script to:
- get IPs of peers connected to Ethereum geth daemon
- get geolocation information of these addresses
- send it to InfluxDB database
...so that it could be used with eg. Grafana Worldmap plugin
https://ethbian.org | https://github.com/ethbian/ethbian/
"""

import os
import datetime
import subprocess

try:
    import geoip2.database
except ImportError:
    raise ImportError('\n\n cannot find Python library: geoip2\n' +
                      ' try executing: pip install geoip2 or apt-get install python-geoip2')
try:
    import influxdb
except ImportError:
    raise ImportError('\n\n cannot find Python library: influxdb\n' +
                      ' try executing: pip install influxdb or apt-get install python-influxdb')

SERVICE = 'geth'
GETH_PATH = '/usr/local/bin/geth/geth'
IPC_PATH = '/mnt/ssd/datadir/geth.ipc'
GEODB_PATH = '/usr/local/lib/collectd/geolite_city.mmdb'

DB_HOST = 'localhost'
DB_NAME = 'collectd'
DB_PORT = 8086
DB_TABLE = 'geth_peers_geo'

for f in [GETH_PATH, IPC_PATH, GEODB_PATH]:
    if not os.path.exists(f):
        raise SystemExit('File {} does not exist.'.format(f))

geth_running = subprocess.call(
    'systemctl is-active --quiet {}'.format(SERVICE), shell=True)
if geth_running != 0:
    raise SystemExit('Service {} is not running.'.format(SERVICE))

try:
    db_client = influxdb.InfluxDBClient(
        host=DB_HOST, port=DB_PORT, database=DB_NAME)
except Exception as e:
    raise SystemExit('Error connecting to database: {}'.format(e))

try:
    admin_peers = subprocess.check_output('{} {}{} {}'.
                                          format(GETH_PATH, 'attach ipc:',
                                                 IPC_PATH, '--exec admin.peers'),
                                          shell=True)
except Exception as e:
    raise SystemExit('Error getting peer list: {}'.format(e))

try:
    geodb = geoip2.database.Reader(GEODB_PATH)
except Exception as e:
    raise SystemExit('Error opening geodb file: {}'.format(e))
peers = []

for line in admin_peers.splitlines():
    peer = {}
    if 'remoteAddress' in line:
        ip = line.split('"')[1].split(':')[0]
        if ip:
            geo = geodb.city(ip)
            peer['measurement'] = DB_TABLE
            peer['time'] = datetime.datetime.utcnow().strftime(
                '%Y-%m-%dT%H:%M:%S.%fZ')
            peer['fields'] = {
                'lat': geo.location.latitude,
                'lon': geo.location.longitude,
                'city': '{} ({} {})'.format(ip, unicode(geo.city.name).encode('utf-8'), geo.registered_country.iso_code)
            }
        peers.append(peer)

try:
    db_client.write_points(peers)
except Exception as e:
    print 'Error writing to database: {}'.format(e)
else:
    print 'Sent {} geth peers to database.'.format(len(peers))

db_client.close()
