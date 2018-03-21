# Simple trading platform
## Parts
### 1. Keycloak - OpenID Connect identity server
two docker images, one for server, one for postgres DB

### 2. Apache Kafka - one image together with zookeeper
This would need persistence (real hdd volumes) and multiple instances to make it resiliant. This is the cornerstone of the platform. 
Kafka is a MQ system that can eliminate potential for dataloss. TODO: Our end needs to cooperate though and store "processed" offsets so resuming will be possible. 

### 3. python jobs:
* engine-processing: Takes orders from MQ and processes the OrderBook
* store-orderbookdata: Keeps the latest orderbook available so API can have it (in DB)
* balance: Keeps tally of executed orders and updates users' profile/wallet

### 4. python api
Simple REST api on python/pyramid. TODO: swagger or similar

### 5. Angular UI
Simple web client, local use for now.

For external access config files would need to be changed.

# Deploy

* Use GNU/Linux
* ansible>=2.4
* npm 8.10
* python ~3.6, virtualenv, pip 
* a member of docker group OR sudo permissions and uncomment # become:true line at the top of run.yml

In case of this error: ``, what it itself suggest usually works, but it might be necessary to install the module using package manager or the module could be named "docker" instead of "docker-py", depends on the distro.  

0. Prepare virtualenv 1 level above this file
1. In folder `./ansible` run `ansible-playbook run.yml`
2. Watch
3. The result should be something like this (though all times will be in minutes/seconds):
    ```
    CONTAINER ID        IMAGE                    COMMAND                  CREATED             STATUS              PORTS                                            NAMES
    517a682f6030        resefex-frontend-image   "nginx -g 'daemon ..."   30 minutes ago      Up 30 minutes       0.0.0.0:8090->80/tcp                             resefex-frontend
    148763e87f73        resefex-keycloak         "/opt/jboss/docker..."   About an hour ago   Up 39 minutes       0.0.0.0:8091->8080/tcp                           resefex-auth
    c8be422c6973        postgres:9               "docker-entrypoint..."   About an hour ago   Up 39 minutes       5432/tcp                                         resefex-auth-db
    21355c7fa9b6        resefex-python-image     "store_orderbookda..."   About an hour ago   Up 39 minutes                                                        resefex-store-orderbookdata
    ac42d6383843        resefex-python-image     "store_balance pro..."   About an hour ago   Up 39 minutes                                                        resefex-store-balance
    d78f51dd3165        resefex-python-image     "processor prod.ini"     About an hour ago   Up 39 minutes                                                        resefex-processor
    108bcf9a275e        resefex-python-image     "pserve prod.ini"        About an hour ago   Up 40 minutes       0.0.0.0:6543->6543/tcp                           resefex-pyramid
    61611bd245fb        spotify/kafka            "supervisord -n"         About an hour ago   Up 40 minutes       0.0.0.0:2181->2181/tcp, 0.0.0.0:9092->9092/tcp   resefex-mq
    92f218e227aa        postgres:9.6             "docker-entrypoint..."   About an hour ago   Up 40 minutes       0.0.0.0:5423->5432/tcp                           resefex-db
    ```
4. Access the UI [http://10.52.52.10](http://10.52.52.10)

    Pre-created users: user1/user1 and user2/user2

5. Create more users: [admin console](http://10.52.52.103:8080/auth/admin/) then also add users to user table in database (TODO auto-create authenticate user entries in db)

# DEV Setup

Same requirements as deploy

1. virtualenv in `../`
2. In folder `./ansible` run `ansible-playbook run-dev.yml`
3. Prepare with `pip install -e .`
4. Prepare the DB: `../bin/initialize_db development.ini`
5. Startup the MQ workers: 
* `../bin/processor development.ini`
* `../bin/store_orderbookdata development.ini`
* `../bin/balance development.ini`
6. Run the API: `pserve development.ini --reload`
7. Prepare the npm: `npm install` and run gui `npm start`
8. Access the UI [http://localhost:4200](http://localhost:4200)
