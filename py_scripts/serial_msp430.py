from curses import baudrate
import paho.mqtt.client as mqtt
from datetime import datetime
import serial


BROKER = 'mqtt.ssh.edu.it'
TOPIC_PUBLISHER = '4F/temperature/group1'
SERIAL_PORT = "/dev/cu.usbmodem2132203" 		#serial port for msp430


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


def on_publish(client, userdata, mid):
	print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] msg published with id: {mid}')
	event_flag = True


def main():
	client = mqtt.Client()

	#events --> callback association
	client.on_connect = on_connect
	client.on_publish = on_publish

	#client --> broker connection
	print('MQTT client connecting...', end = ' ')
	client.connect(BROKER)

	client.loop_start()

	#wait and listen for events (ctrl-c to quit)
	try:
		while True:
			final_msg = ''
			while ser.inWaiting() > 0:	#if there's something to read from serial (bytes)
				final_msg += ser.read().decode("ascii")
			
			if final_msg != '':
				client.publish(TOPIC_PUBLISHER,final_msg)


	except KeyboardInterrupt:
			print('\nMQTT client disconnecting...bye')
	finally:
		client.disconnect()
		client.loop_stop()
		ser.close()

if __name__ == '__main__':
	main()