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
Simple web client

# Deploy

0. Use GNU/Linux; ansible>=2.4, npm
1. In folder `./ansible` run `ansible-playbook run.yml`
2. Watch
3. The result should be something like this (though all times will be in minutes/seconds):
    ```
    9b5d5d6b2ea9        resefex-frontend-image   "nginx -g 'daemon ..."   6 minutes ago       Up 6 minutes        0.0.0.0:8090->80/tcp                             resefex-frontend
    2736e7dfbbbd        python-image             "store_orderbookda..."   28 minutes ago      Up 17 minutes                                                        resefex-store-orderbookdata
    764d2578edc5        python-image             "store_balance dev..."   28 minutes ago      Up 28 minutes                                                        resefex-store-balance
    0048f13ca089        python-image             "processor develop..."   29 minutes ago      Up 29 minutes                                                        resefex-processor
    5a09e73d989f        python-image             "pserve developmen..."   29 minutes ago      Up 29 minutes       0.0.0.0:6543->6543/tcp                           resefex-pyramid
    4668c74c65c7        postgres:9.6             "docker-entrypoint..."   4 days ago          Up 30 minutes       0.0.0.0:5423->5432/tcp                           resefex-db
    be43c77b32f5        spotify/kafka            "supervisord -n"         4 days ago          Up 30 minutes       0.0.0.0:2181->2181/tcp, 0.0.0.0:9092->9092/tcp   resefex-mq
    ```
4. Access the UI [http://10.52.52.10](http://10.52.52.10)

    Pre-created users: user1/user1 and user2/user2

5. Create more users: [admin console](http://10.52.52.103:8080/auth/admin/) then also add users to user table in database (TODO auto-create authenticate user entries in db)

# DEV Setup

0. Use GNU/Linux; Python ~3.6, ansible>=2.4, npm
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

TODO: orderbook.service.ts API ips won't work for this setup :(
