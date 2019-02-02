#################
ttnlogger Grafana
#################


*******
Plugins
*******
::

    git clone https://github.com/pR0Ps/grafana-trackmap-panel

    cd grafana-trackmap-panel
    npm install
    npm run build

    ln -s `pwd` /usr/local/var/lib/grafana/plugins/


::

    git clone https://github.com/JamesOsgood/mongodb-grafana

    cd mongodb-grafana
    npm install
    npm run server

    ln -s `pwd` /usr/local/var/lib/grafana/plugins/

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
::

    http --session=grafana http://localhost:3000/ --auth=admin:admin

Create datasource::

    cat ttnlogger/grafana/datasource.json | http --session=grafana POST http://localhost:3000/api/datasources

Create dashboard::

    cat ttnlogger/grafana/dashboard.json | http --session=grafana POST http://localhost:3000/api/dashboards/db
