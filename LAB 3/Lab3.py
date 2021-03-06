import paho.mqtt.client as mqttclient
import time
import json
import serial.tools.list_ports

print("IoT Gateway")

BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
mess = ""



THINGS_BOARD_ACCESS_TOKEN = "7c37e2ZNhzPFA99lWnVC" 
bbc_port = "COM3"

if len(bbc_port) > 0:
    ser = serial.Serial(port=bbc_port, baudrate=115200)

def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    processedData = dict();
    #TODO: Add your source code to publish data to the server
    if(splitData[1] == "TEMP"):
        processedData["temperature"] = splitData[-1];

    elif (splitData[1] == "LIGHT"):
        processedData["light"] = splitData[-1];

    client.publish('v1/devices/me/telemetry',json.dumps(processedData),1)
    return;


def readSerial():
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")

def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = dict()
    cmd = -1
 # TODO: Update the cmd to control 2 devices
    global ledSignal, fanSignal
    try:
        jsonobj = json.loads(message.payload)
        print(jsonobj);

        if jsonobj['method'] == "setLED":
            temp_data['led'] = jsonobj['params']
            ledSignal = jsonobj['params']
            client.publish('v1/devices/me/attributes',
                    json.dumps(temp_data), 1)
        if jsonobj['method'] == "setFAN":
            temp_data['fan'] = jsonobj['params']
            fanSignal = jsonobj['params']
            client.publish('v1/devices/me/attributes',
                    json.dumps(temp_data), 1)

        if ledSignal and fanSignal:
            cmd = 0
        if ledSignal and not fanSignal:
            cmd = 1
        if not ledSignal and fanSignal:
            cmd = 2
        if not ledSignal and not fanSignal:
            cmd = 3

    except:
        pass

    if len(bbc_port) > 0:
        ser.write((str(cmd) + "#").encode())



def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")


client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message

while True:

    if len(bbc_port) >  0:
        readSerial()

    time.sleep(0.5)