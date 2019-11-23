#########
ttnlogger
#########


*****
About
*****
TTN data logger made with FiPy_, MQTT_, InfluxDB_, MongoDB_ and Grafana_.

TTN (`The Things Network`_) is building a global open LoRaWAN™ network.


********
Synopsis
********
The ``ttnlogger`` program can be invoked in two ways. Either it obtains four
positional arguments on the command line or it obtains the four parameters
from respective environment variables.


Command line arguments
----------------------
::

    ttnlogger "<ttn_app_id>" "<ttn_access_key>" "<influxdb_database>" "<influxdb_measurement>"


Environment variables
---------------------
::

    export TTN_APP_ID="testdrive"
    export TTN_ACCESS_KEY="ttn-account-v2.UcOZ3_gRRVbzsJ1lR7WfuINLN_DKIlc9oKvgukHPGck"
    export INFLUXDB_DATABASE="test"
    export INFLUXDB_MEASUREMENT="data"

    ttnlogger


*****
Setup
*****
::

    git clone https://github.com/daq-tools/ttnlogger /opt/ttnlogger
    /opt/ttnlogger
    virtualenv --python=python3 .
    python setup.py develop


Run as systemd unit::

    cp etc/default/ttnlogger /etc/default/
    ln -sr etc/systemd/ttnlogger.service /usr/lib/systemd/system/

    # Edit configuration file
    nano /etc/default/ttnlogger

    systemctl enable ttnlogger
    systemctl start ttnlogger
    systemctl status ttnlogger
    journalctl -u ttnlogger -f



.. _The Things Network: https://www.thethingsnetwork.org/
.. _FiPy: https://pycom.io/product/fipy/
.. _MQTT: https://mqtt.org/
.. _InfluxDB: https://github.com/influxdata/influxdb
.. _MongoDB: https://github.com/mongodb/mongo
.. _Grafana: https://github.com/grafana/grafana
