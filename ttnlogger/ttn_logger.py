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


class TTNDatenpumpe:

    def __init__(self, ttn=None, influxdb=None, mongodb=None):
        self.ttn = ttn
        self.influxdb = influxdb
        self.mongodb = mongodb

    def on_receive(self, message=None, client=None):
        #print('on_receive:', message, client)
        try:
            self.influxdb.store(message)
        except Exception as ex:
            print('ERROR:', ex)

    def enable(self):
        self.ttn.receive_callback = self.on_receive
        while True:
            time.sleep(2)


class TTNClient:

    def __init__(self, app_id, access_key):
        self.app_id = app_id
        self.access_key = access_key
        self.receive_callback = None
        self.connect()

    def connect(self):
        print('Connecting to TTN MQTT broker')
        handler = ttn.HandlerClient(self.app_id, self.access_key)

        # using mqtt client
        mqtt_client = self.mqtt_client = handler.data()
        mqtt_client.set_connect_callback(self.connect_callback)
        mqtt_client.set_uplink_callback(self.uplink_callback)
        mqtt_client.connect()

    def disconnect(self):
        self.mqtt_client.close()

    def connect_callback(self, res, client):
        address = client._MQTTClient__mqtt_address
        print('Connected to MQTT broker at "{}"'.format(address))

    def uplink_callback(self, msg, client):
        print('-' * 63)
        print('Received uplink message from device "{}"'.format(msg.dev_id))
        if self.receive_callback is not None:
            self.receive_callback(message=msg, client=client)


class InfluxDatabase:

    def __init__(self, database=None):
        self.database = database
        self.connect()

    def connect(self):
        self.client = InfluxDBClient('localhost', 8086, 'root', 'root', self.database)
        self.client.create_database(self.database)

    def store(self, ttn_message):

        #print('ttn_message:', ttn_message)

        name = 'data'
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
    app_id = os.getenv('TTN_APP_ID') or sys.argv[1]
    access_key = os.getenv('TTN_ACCESS_KEY') or sys.argv[2]

    ttn = TTNClient(app_id, access_key)
    influxdb = InfluxDatabase('ttnlogger')

    datenpumpe = TTNDatenpumpe(ttn, influxdb)
    datenpumpe.enable()
