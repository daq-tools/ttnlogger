#################
ttnlogger Grafana
#################


*******
Plugins
*******
::

    git clone https://github.com/pR0Ps/grafana-trackmap-panel
    ln -s `pwd`/grafana-trackmap-panel /usr/local/var/lib/grafana/plugins/

    cd grafana-trackmap-panel
    npm install
    npm run build


::

    git clone https://github.com/JamesOsgood/mongodb-grafana
    ln -s `pwd`/mongodb-grafana /usr/local/var/lib/grafana/plugins/

    cd mongodb-grafana
    npm install
    npm run server


List plugins::

    grafana-cli --pluginsDir=/usr/local/var/lib/grafana/plugins plugins ls


*******
Running
*******
::


    make grafana-start



*********
Configure
*********
Create datasource::

    http --session=grafana http://localhost:3000/ --auth=admin:admin
    cat ttnlogger/grafana/datasource-influxdb.json | http --session=grafana POST http://localhost:3000/api/datasources

Create dashboard::

    # TODO
