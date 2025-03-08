import argparse
import os
import logging

from google.protobuf.json_format import MessageToJson
import paho.mqtt.client as mqtt

import proto.pr705_pb2 as pr705_pb2
import proto.Common_pb2 as Common_pb2


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


# Define a custom argparse action to set the default value of an argument from environment variable
class EnvDefault(argparse.Action):
    def __init__(self, envvar, required=True, default=None, **kwargs):
        if envvar:
            if envvar in os.environ:
                default = os.environ[envvar]
        if required and default:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required, 
                                         **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


def parse_protobuf_msg(payload):
    dpu = pr705_pb2.DisplayPropertyUpload()
    header = Common_pb2.Send_Header_Msg()
    numRead = header.ParseFromString(payload)
    logging.info(f"number of bytes Read: {numRead}")
    logging.info(f"header: {header}")

    for m in header.msg:
        if m.cmd_id == 21:
            data = m.pdata
            try:
                dpu.ParseFromString(data)
                logging.info(f"DisplayPropertyUpload: {MessageToJson(dpu)}")
            except Exception as e:
                logging.error(f"Error parsing DisplayPropertyUpload: {e}; hex data: {data.hex()}")


# Define the callback function for when a message is received
def on_message(client, userdata, message):
    try:
        # try to print the message payload as json
        logging.info(f"Received message: {message.payload.decode()} on topic {message.topic}")
    except Exception as e:
        logging.error(f"Error decoding message: {e}")
        # try to decode with protobuf
        parse_protobuf_msg(message.payload)
    logging.info(f"Saving message to file")
    with open("message.txt", "wb") as file:
        file.write(message.payload)
    logging.info(f"Message QoS: {message.qos}")
    logging.info(f"Message retain flag: {message.retain}")


parser = argparse.ArgumentParser()
parser.add_argument("--username", action=EnvDefault, envvar="MQTT_USERNAME", help="MQTT username")
parser.add_argument("--password", action=EnvDefault, envvar="MQTT_PASSWORD", help="MQTT password")
parser.add_argument("--broker", default="mqtt.ecoflow.com")
parser.add_argument("--port", default=8883)
parser.add_argument("--device_id", action=EnvDefault, envvar="DEVICE_ID", help="Device ID")
parser.add_argument("--account_id", action=EnvDefault, envvar="ACCOUNT_ID", help="Account ID")
parser.add_argument("--read-local", action="store", help="Read a single MQTT message from local file instead of from MQTT")
args = parser.parse_args()

if args.read_local:
    with open("message.txt", "rb") as file:
        message = file.read()

    parse_protobuf_msg(message)
    exit(0)


if not args.username:
    parser.error("MQTT username is required")
if not args.password:
    parser.error("MQTT password is required")
if not args.device_id:
    parser.error("Device ID is required")
if not args.account_id:
    parser.error("Account ID is required")

# Define the MQTT broker details
broker = args.broker
port = args.port
start_topic = f"/app/{args.account_id}/{args.device_id}/thing/property/get_reply"
metric_topic = f"/app/device/property/{args.device_id}"

# Create an MQTT client instance
client = mqtt.Client(
    # callback_api_version=1,
    client_id="ANDROID_EDIERR12AD_1887309584504352769",
    clean_session=True,
)

client.username_pw_set(
    username=args.username,
    password=args.password,
)

# Assign the on_message callback function
client.on_message = on_message

client.tls_set()

client

client.enable_logger()

# Connect to the MQTT broker
client.connect(broker, port)

# Subscribe to the topic
client.subscribe(metric_topic, qos=0)

# Start the MQTT client loop to process network traffic and dispatch callbacks
client.loop_forever()