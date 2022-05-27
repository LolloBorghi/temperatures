## this import is about mqtt
import time
from keys import API_TOKEN, PRIVATE_ORG     #contains private values
import paho.mqtt.client as mqtt
from datetime import datetime

## this import is about dbms
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS


#####################
## SETUP DBMS

# You can generate an API token from the "API Tokens Tab" in the UI
bucket = "gruppo1"
org = PRIVATE_ORG
token = API_TOKEN
# Store the URL of your InfluxDB instance
url="https://us-east-1-1.aws.cloud2.influxdata.com"


client = influxdb_client.InfluxDBClient(
   url=url,
   token=token,
   org=org
)

write_api = client.write_api(write_options=SYNCHRONOUS)


#####################
## SETUP MQTT

BROKER = 'mqtt.ssh.edu.it'
TOPIC_SUBSCRIBER = '4F/temperature/group1'


def on_connect(client, userdata, flags, rc):
	print(f'{mqtt.connack_string(rc)}')
	event_flag = True


def on_subscribe(client, userdata, mid, granted_qos):
	print(f'subscribed {TOPIC_SUBSCRIBER} with QoS: {granted_qos[0]}\n')


def on_message(client, userdata, msg):
    msg_decode = str(msg.payload.decode("utf-8"))
    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] received: {msg_decode} from topic: {msg.topic}')
    
    #when the temperature arrives, we load it into the dbms server
    p = influxdb_client.Point("temperatures").tag("device", "MSP430F5529").tag("group", "1").field("temp", msg_decode)
    write_api.write(bucket=bucket, org=org, record=p)


def main():
    client = mqtt.Client()

	#events --> callback association
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message

	#client --> broker connection
    print('MQTT client connecting...', end = ' ')
    client.connect(BROKER)
    client.subscribe(TOPIC_SUBSCRIBER)
    client.loop_start()


    try:
        while True:
            pass    #listening
            
    except KeyboardInterrupt:
        print('\nMQTT client disconnecting...bye')
    finally:
        client.disconnect()
        client.loop_stop()

if __name__ == '__main__':
    main()