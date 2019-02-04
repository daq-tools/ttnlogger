#################
ttnlogger Grafana
#################


*******
Plugins
*******
::

    # Get sources
    git clone https://github.com/pR0Ps/grafana-trackmap-panel

    # Run build
    cd grafana-trackmap-panel
    npm install
    npm run build

    # Install as Grafana plugin
    ln -s `pwd` /var/lib/grafana/plugins/

List all installed plugins::

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
