## install ssdb

```
wget --no-check-certificate https://github.com/ideawu/ssdb/archive/master.zip
unzip master
cd ssdb-master
make
# optional, install ssdb in /usr/local/ssdb
sudo make install
```

## start ssdb server

```
# start master
./ssdb-server ssdb.conf

# or start as daemon
./ssdb-server -d ssdb.conf
```

## use redis client to connection ssdb server

```
import redis
r = redis.Redis(host='localhost', port=8888, db=0)
print(r.set('foo', 'bar'))
print(r.get('foo'))

```


## product setting

