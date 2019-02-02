#########
ttnlogger
#########


*****
About
*****
TTN data logger made with FiPy_, MQTT_, InfluxDB_ and Grafana_.


********
Synopsis
********

Interactive
-----------
::

    ttnlogger "{app_id}" "{access_key}"


w/o arguments
-------------
::

    export TTN_APP_ID="{app_id}"
    export TTN_ACCESS_KEY="{access_key}"

    ttnlogger


*****
Setup
*****

Run as systemd unit::

    ln -sr etc/default/ttnlogger /etc/default/
    ln -sr etc/systemd/ttnlogger.service /usr/lib/systemd/system/

    systemctl enable ttnlogger
    systemctl start ttnlogger
    systemctl status ttnlogger
    journalctl -f ttnlogger



.. _FiPy: https://pycom.io/product/fipy/
.. _MQTT: https://mqtt.org/
.. _InfluxDB: https://github.com/influxdata/influxdb
.. _Grafana: https://github.com/grafana/grafana
