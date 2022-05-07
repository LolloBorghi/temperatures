from curses import baudrate
import paho.mqtt.client as mqtt
from datetime import datetime
import serial

BROKER = 'mqtt.ssh.edu.it'
TOPIC_PUBLISHER = '4F/temperature/group1'
#TOPIC_SUBSCRIBER = 'crono/borghi/command'
SERIAL_PORT = "/dev/cu.usbmodem2132203"                      #inserire la porta seriale per msp430


try:
	ser = serial.Serial(SERIAL_PORT,baudrate=9600)
	ser.close()
	ser.open()
except:
	print(f"can't reach serial on {SERIAL_PORT}")
	exit

def on_connect(client, userdata, flags, rc):
	print(f'{mqtt.connack_string(rc)}')
	event_flag = True

'''
def on_subscribe(client, userdata, mid, granted_qos):
	print(f'subscribed {TOPIC_SUBSCRIBER} with QoS: {granted_qos[0]}\n')
'''

'''
def on_message(client, userdata, msg):
	msg_decode = msg.payload.decode("utf-8")
	print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] received: {msg.payload.decode("utf-8")} from topic: {msg.topic}')
    # with serial.Serial(SERIAL_PORT,baudrate=9600) as ser:
	print("invio in seriale il messaggio "+msg_decode)
	if msg_decode == "START":
		ser.write('s'.encode("ascii"))	#START
	elif msg_decode == "STOP":
		ser.write('p'.encode("ascii"))	#STOP
	else:
		ser.write('r'.encode("ascii"))	#RESET
'''

def on_publish(client, userdata, mid):
	print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] msg published with id: {mid}')
	event_flag = True

def main():
	client = mqtt.Client()
	#events --> callback association
	client.on_connect = on_connect
	#client.on_subscribe = on_subscribe
	#client.on_message = on_message
	client.on_publish = on_publish

	#client --> broker connection
	print('MQTT client connecting...', end = ' ')
	client.connect(BROKER)
	#client.subscribe(TOPIC_SUBSCRIBER)
	client.loop_start()

	#wait and listen for events (ctrl-c to quit)
	try:
		while True:
			final_msg = ''
			while ser.inWaiting() > 0:	#se c'è qualcosa da leggere
				final_msg += ser.read().decode("ascii")
			
			if final_msg != '':
				client.publish(TOPIC_PUBLISHER,final_msg)


	except KeyboardInterrupt:
			print('\nMQTT client disconnecting...bye')
	finally:
		client.disconnect()

if __name__ == '__main__':
	main()