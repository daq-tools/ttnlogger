# -*- coding: utf-8 -*-
# (c) 2019 Andreas Motl <andreas@hiveeyes.org>
# License: GNU Affero General Public License, Version 3
import os
import sys
import ttn
import time
import json
from influxdb import InfluxDBClient
from collections import OrderedDict

from ttnlogger.util import convert_floats


class TTNDatenpumpe:

    def __init__(self, ttn=None, influxdb=None, mongodb=None):
        self.ttn = ttn
        self.mongodb = mongodb

    def on_receive(self, message=None, client=None):
        #print('on_receive:', message, client)

        influxdb_env = message.dev_id.split('-')
        influxdb_database = '_'.join(influxdb_env[:2])
        influxdb_measurement = '_'.join(influxdb_env[2:])

        #print('influxdb_database    :', influxdb_database)
        #print('influxdb_measurement :', influxdb_measurement)

        try:
            del self.influxdb
        except Exception as ex:
            print('ERROR: Could not delete InfluxDB object', ex)

        self.influxdb = InfluxDatabase(database=influxdb_database, measurement=influxdb_measurement)

        try:
            self.influxdb.store(message)
        except Exception as ex:
            print('ERROR:', ex)

    def enable(self):
        self.ttn.receive_callback = self.on_receive
        while True:
            print('Connected:', self.ttn.connected)
            time.sleep(5)


class TTNClient:

    def __init__(self, app_id, access_key):
        self.app_id = app_id
        self.access_key = access_key
        self.receive_callback = None
        self.mqtt_client = None
        self.connected = False
        self.connect()

    def connect(self):
        print('Connecting to TTN MQTT broker')
        handler = ttn.HandlerClient(self.app_id, self.access_key)

        # Start MQTT client and wire event callbacks.
        mqtt_client = self.mqtt_client = handler.data()
        mqtt_client._MQTTClient__client.enable_logger()
        mqtt_client.set_connect_callback(self.connect_callback)
        mqtt_client.set_close_callback(self.disconnect_callback)
        mqtt_client.set_uplink_callback(self.uplink_callback)
        mqtt_client.connect()

    def connect_callback(self, res, client):
        address = client._MQTTClient__mqtt_address
        print('Connected to MQTT broker at "{}"'.format(address))
        self.connected = True

    def disconnect_callback(self, res, client):
        address = client._MQTTClient__mqtt_address
        print('Disconnected from MQTT broker at "{}"'.format(address))
        self.connected = False

    def uplink_callback(self, msg, client):
        print('-' * 63)
        print('Received uplink message from device "{}"'.format(msg.dev_id))
        if self.receive_callback is not None:
            self.receive_callback(message=msg, client=client)


class InfluxDatabase:

    def __init__(self, database='ttnlogger', measurement='data'):

        assert database, 'Database name missing or empty'
        assert measurement, 'Measurement name missing or empty'

        self.database = database
        self.measurement = measurement
        self.connect()

    def connect(self):
        self.client = InfluxDBClient('localhost', 8086, 'root', 'root', self.database)
        self.client.create_database(self.database)

    def store(self, ttn_message):

        #print('ttn_message:', ttn_message)

        name = self.measurement
        data = OrderedDict()

        # Pick up telemetry values from main data payload.
        for field in ttn_message.payload_fields._fields:
            if field in ['raw', 'hexstring']: continue
            value = getattr(ttn_message.payload_fields, field)
            data[field] = value

        # Pick up telemetry values from gateway information.
        gw0 = ttn_message.metadata.gateways[0]
        data['gw_rssi'] = float(gw0.rssi)
        data['gw_snr'] = float(gw0.snr)
        data['gw_latitude'] = float(gw0.latitude)
        data['gw_longitude'] = float(gw0.longitude)
        data['gw_altitude'] = float(gw0.altitude)

        # Convert all numeric values to floats.
        data = convert_floats(data)

        # Add application and device id as tags.
        tags = OrderedDict()
        tags['app_id'] = ttn_message.app_id
        tags['dev_id'] = ttn_message.dev_id

        point = {
            "measurement": name,
            "tags": tags,
            "time": ttn_message.metadata.time,
            "fields": data,
        }
        print(json.dumps(point))
        self.client.write_points([point])


def run():
    try:
        ttn_app_id = os.getenv('TTN_APP_ID') or sys.argv[1]
        ttn_access_key = os.getenv('TTN_ACCESS_KEY') or sys.argv[2]

    except IndexError:
        print('ERROR: Missing arguments. Either provide them using '
              'environment variables or as positional arguments.')
        sys.exit(1)

    ttn = TTNClient(ttn_app_id, ttn_access_key)

    datenpumpe = TTNDatenpumpe(ttn)
    datenpumpe.enable()
