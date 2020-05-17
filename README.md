# tabular

🎵 Tabular, we're gonna make you tab-yoo-hoo-lar 🎵

Parse ASCII tabular data, such as the output from `docker ps` or `netstat -tanp`.

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-black.svg)](https://snapcraft.io/tabular)

```bash
$ docker ps
CONTAINER ID        IMAGE                      COMMAND                  CREATED             STATUS              PORTS                                                                       NAMES
a5b04a56f27c        docker_dashboard           "npm start"              3 days ago          Up 28 minutes       127.0.0.1:4000->4000/tcp, 5858/tcp                                          docker_dashboard_1
7755ce972c33        docker_crawler             "docker-entrypoint.s…"   3 days ago          Up 28 minutes       0.0.0.0:3000->3000/tcp, 5858/tcp                                            docker_crawler_1

$ docker ps | python3 tabular.py 
CONTAINER ID=a5b04a56f27c
IMAGE=docker_dashboard
COMMAND="npm start"
CREATED=3 days ago
STATUS=Up 28 minutes
PORTS=127.0.0.1:4000->4000/tcp, 5858/tcp
NAMES=docker_dashboard_1

CONTAINER ID=7755ce972c33
IMAGE=docker_crawler
COMMAND="docker-entrypoint.s…"
CREATED=3 days ago
STATUS=Up 28 minutes
PORTS=0.0.0.0:3000->3000/tcp, 5858/tcp
NAMES=docker_crawler_1

# or as JSON
$ docker ps | python3 tabular.py --format=json
[
  {
    "CONTAINER ID": "a5b04a56f27c",
    "IMAGE": "docker_dashboard",
    "COMMAND": "\"npm start\"",
    "CREATED": "3 days ago",
    "STATUS": "Up 29 minutes",
    "PORTS": "127.0.0.1:4000->4000/tcp, 5858/tcp",
    "NAMES": "docker_dashboard_1"
  },
  {
    "CONTAINER ID": "7755ce972c33",
    "IMAGE": "docker_crawler",
    "COMMAND": "\"docker-entrypoint.s\u2026\"",
    "CREATED": "3 days ago",
    "STATUS": "Up 29 minutes",
    "PORTS": "0.0.0.0:3000->3000/tcp, 5858/tcp",
    "NAMES": "docker_crawler_1"
  }
]


$ netstat -tanp
Active Internet connections (servers and established)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name    
tcp        0      0 127.0.0.1:4000          0.0.0.0:*               LISTEN      -                   
tcp        0      0 127.0.0.1:17600         0.0.0.0:*               LISTEN      9244/dropbox        
tcp        0      0 127.0.0.1:17603         0.0.0.0:*               LISTEN      9244/dropbox        
tcp        0      0 0.0.0.0:902             0.0.0.0:*               LISTEN      - 

# note that netstat adds an extra line to the output before the table
# so we skip it.
$ netstat -tanp | python3 tabular.py --skip=1
Proto=tcp
Recv-Q=0
Send-Q=0
Local Address=127.0.0.1:4000
Foreign Address=0.0.0.0:*
State=LISTEN
PID/Program name=-

Proto=tcp
Recv-Q=0
Send-Q=0
Local Address=127.0.0.1:17600
Foreign Address=0.0.0.0:*
State=LISTEN
PID/Program name=9244/dropbox

Proto=tcp
Recv-Q=0
Send-Q=0
Local Address=127.0.0.1:17603
Foreign Address=0.0.0.0:*
State=LISTEN
PID/Program name=9244/dropbox

Proto=tcp
Recv-Q=0
Send-Q=0
Local Address=0.0.0.0:902
Foreign Address=0.0.0.0:*
State=LISTEN
PID/Program name=-
```

