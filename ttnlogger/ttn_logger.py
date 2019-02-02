import sys
import ttn
import time
from influxdb import InfluxDBClient
from collections import OrderedDict


class TTNDatenpumpe:

    def __init__(self, ttn=None, influxdb=None, mongodb=None):
        self.ttn = ttn
        self.influxdb = influxdb
        self.mongodb = mongodb

    def on_receive(self, message=None, client=None):
        print('on_receive:', message, client)
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
        handler = ttn.HandlerClient(self.app_id, self.access_key)

        # using mqtt client
        mqtt_client = self.mqtt_client = handler.data()
        mqtt_client.set_connect_callback(self.connect_callback)
        mqtt_client.set_uplink_callback(self.uplink_callback)
        mqtt_client.connect()

    def disconnect(self):
        self.mqtt_client.close()

    def connect_callback(self, res, client):
      print("Connected to MQTT:", res)

    def uplink_callback(self, msg, client):
      print("Received uplink from device", msg.dev_id)
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

        name = ttn_message.dev_id + '_sensors'
        data = OrderedDict()

        for field in ttn_message.payload_fields._fields:
            print('field:', field)
            if field in ['raw', 'hexstring']: continue
            value = getattr(ttn_message.payload_fields, field)
            data[field] = value

        influx_points = [
            {
                "measurement": name,
                "tags": {
                },
                "time": ttn_message.metadata.time,
                "fields": data,
            }
        ]
        print('influx_points:', influx_points)
        self.client.write_points(influx_points)


def run():
    app_id = sys.argv[1]
    access_key = sys.argv[2]

    ttn = TTNClient(app_id, access_key)
    influxdb = InfluxDatabase('ttn_testdrive')

    datenpumpe = TTNDatenpumpe(ttn, influxdb)
    datenpumpe.enable()
