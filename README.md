# geth_peers_geo2influx
A python script to list ethereum geth peers IPs, get their geolocation and send it to InfluxDB

## dependencies
- **geoip2** python library  
  *apt-get install python-geoip2* or  
  *pip install geoip2*  
- **influxdb** python library  
  *apt-get install python-influxdb* or  
  *pip install influxdb*  
- **GeoLite2 City** free database  
  [https://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz](https://geolite.maxmind.com/download/geoip/database/GeoLite2-City.tar.gz)


## quick start
- edit the file and make sure paths to files are correct
- the script requires geth server to be running
- geolocation information is sent to Influx database
- the data can be used by eg. Grafana Worldmap plugin
- the script should be executed periodically as a crob job


## data format

    > select * from geth_peers_geo limit 5;
    name: geth_peers_geo
    time                city                               lat     lon
    ----                ----                               ---     ---
    1575737543016009984 5.187.1.xyz (Frankfurt am Main DE) 50.1188 8.6843
    1575737543016866048 13.229.153.xyz (Singapore SG)      1.2929  103.8547
    1575737543017404928 93.115.24.xyz (None LT)             56      24
    1575737543027055104 47.52.35.xyz (None CN)             22.25   114.1667
    1575737543027645952 95.216.246.xyz (None FI)           60.1717 24.9349

## use case
Here's a [screenshot](https://ethbian.org/images/grafana_worldmap_plugin.png) of Grafana Worldmap plugin using provided data.

Pull requests are more than welcome if you're fixing something