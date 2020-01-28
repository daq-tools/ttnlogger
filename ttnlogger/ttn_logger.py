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
import argparse

from ttnlogger.util import convert_floats


class TTNDatenpumpe:

    def __init__(self, ttn=None, influxdb=None, mongodb=None, nogeo=False, split=False):
        self.ttn = ttn
        self.influxdb = influxdb
        self.mongodb = mongodb
        self.split = split
        self.nogeo = nogeo

    def on_receive(self, message=None, client=None):
        #print('on_receive:', message, client)

        if self.split:
            influxdb_env = message.dev_id.split('-')
            influxdb_database = '_'.join(influxdb_env[:2])
            influxdb_measurement = '_'.join(influxdb_env[2:])

            print('influxdb_database     :', influxdb_database)
            print('influxdb_measurement  :', influxdb_measurement)

            self.influxdb = InfluxDatabase(database=influxdb_database, measurement=influxdb_measurement, nogeo=self.nogeo)

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

    def __init__(self, database='ttnlogger', measurement='data', nogeo=False):

        assert database, 'Database name missing or empty'
        assert measurement, 'Measurement name missing or empty'

        self.database = database
        self.measurement = measurement
        self.nogeo = nogeo
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
        num_gtws = len(ttn_message.metadata.gateways)
        print('Message received from ' + str(num_gtws) + ' gateway(s)')

        for i in range(num_gtws):
            gtw_id = ttn_message.metadata.gateways[i].gtw_id
            print('Gateway ' + str(i+1) + ' ID          : ' + gtw_id)

            # signal quality
            key_rssi = 'gw_' + gtw_id + '_rssi'
            key_snr  = 'gw_' + gtw_id + '_snr'
            data[key_rssi] = int(ttn_message.metadata.gateways[i].rssi)
            data[key_snr]  = float(ttn_message.metadata.gateways[i].snr)

            # gateway location
            if not self.nogeo:
                key_lat  = 'gw_' + gtw_id + '_lat'
                key_lon  = 'gw_' + gtw_id + '_lon'
                key_alt  = 'gw_' + gtw_id + '_alt'
                data[key_lat] = float(ttn_message.metadata.gateways[i].latitude)
                data[key_lon] = float(ttn_message.metadata.gateways[i].longitude)
                data[key_alt] = float(ttn_message.metadata.gateways[i].altitude)

        data['sf'] = int(ttn_message.metadata.data_rate.split('BW')[0][2:])
        data['bw'] = int(ttn_message.metadata.data_rate.split('BW')[1])

        data['gtw_count'] = int(num_gtws)

        # Convert all numeric values to floats.
        data = convert_floats(data, integers=["gtw_count", "sf", "bw"])

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
    parser = argparse.ArgumentParser(description='Subscribe to TTN MQTT topic and write data to InfluxDB')
    parser.add_argument('-i', '--ttn_app_id', dest='ttn_app_id', action='store', required=True)
    parser.add_argument('-k', '--ttn_access_key', dest='ttn_access_key', action='store', required=True)
    parser.add_argument('-s', '--split-topic', dest='split', action='store_true', default=False, help='Get InfluxDB database and measurement from MQTT topic split. If not set provide with --database and --measurement')
    parser.add_argument('-d', '--database', dest='influxdb_database', action='store', help='InfluxDB database')
    parser.add_argument('-m', '--measurement', dest='influxdb_measurement', action='store', help='InfluxDB measurement')
    parser.add_argument('-n', '--no-gw-location', dest='nogeo', action='store_true', default=False, help='Discard geolocation of receiving gateways. Default is False')

    options = parser.parse_args()

    ttn_app_id = os.getenv('TTN_APP_ID') or options.ttn_app_id
    ttn_access_key = os.getenv('TTN_ACCESS_KEY') or options.ttn_access_key
    influxdb_database = os.getenv('INFLUXDB_DATABASE') or options.influxdb_database
    influxdb_measurement = os.getenv('INFLUXDB_MEASUREMENT') or options.influxdb_measurement

    # print('TTN_APP_ID     : ', ttn_app_id)
    # print('TTN_ACCESS_KEY : ', ttn_access_key)
    # print('Split topic    : ', options.split)
    # print('InfluxDB DB    : ', influxdb_database)
    # print('InfluxDB MEAS  : ', influxdb_measurement)
    # print('NO GW LOC      : ', options.nogeo)

    if not options.split and ( influxdb_database is None or influxdb_measurement is None ):
        parser.error('Missing -s requires --database and --measurement options. See -h for help.')
        sys.exit(1)

    ttn = TTNClient(ttn_app_id, ttn_access_key)

    if options.split:
        datenpumpe = TTNDatenpumpe(ttn, nogeo=options.nogeo, split=True)
    else:
        influxdb = InfluxDatabase(database=influxdb_database, measurement=influxdb_measurement, nogeo=options.nogeo)
        datenpumpe = TTNDatenpumpe(ttn, influxdb, nogeo=options.nogeo, split=False)

    datenpumpe.enable()
