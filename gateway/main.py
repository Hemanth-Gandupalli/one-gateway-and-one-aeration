from mqtt_update import MqttConnect
import time
from datetime import datetime
from random import uniform
import json
from paho.mqtt.client import Client
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(23, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(5, GPIO.OUT, initial=GPIO.HIGH)

delay_main = 2
delay_device = 600
last_device_off = time.time()

mq = MqttConnect()
mq.topic = ["661526019560586","324164884510875"]
mqttBroker = "4.240.114.7"
port = 1883
username = "BarifloLabs"
password = "Bfl@123"


def post_data_to_publish():
    mq.connect_to_broker()
    while True:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('status.txt','r') as f:
            status = f.read()
        if status == "True":
            try:
                with open ("data.json",'r') as f:
                    data = json.load(f)
                sensor1 = data["sensor1"]
                sensor2 = data["sensor2"]
                sensor3 = data["sensor3"]
                sensor4 = data["sensor4"]
                X = data["x"]
                Y = data["y"]
                Z = data["z"]
            except Exception as e:
                print(e)
        if status == "False":
                sensor1 = 0
                sensor2 = 0
                sensor3 = 0
                sensor4 = 0
                X = 0
                Y = 0
                Z = 0
            
        for i in mq.topic:
            
            mq.data_publish({"dataPoint": now, "paramType": 'Sensor1', "paramValue": sensor1, "deviceId": i})
            mq.data_publish({"dataPoint": now, "paramType": 'Sensor2', "paramValue": sensor2, "deviceId": i})
            mq.data_publish({"dataPoint": now, "paramType": 'Sensor3', "paramValue": sensor3, "deviceId": i})
            mq.data_publish({"dataPoint": now, "paramType": 'Sensor4', "paramValue": sensor4, "deviceId": i})
            mq.data_publish({"dataPoint": now, "paramType": 'X', "paramValue": X, "deviceId": i})
            mq.data_publish({"dataPoint": now, "paramType": 'Y', "paramValue": Y, "deviceId": i})
            mq.data_publish({"dataPoint": now, "paramType": 'Z', "paramValue": Z, "deviceId": i})
            
        time.sleep(5)
        
def data_subscribe():
    mqtt_client = Client()
    mqtt_client.on_connect = mq.on_connect
    print(mq.on_connect)
    mqtt_client.on_message = mq.on_sub_message
    mqtt_client.username_pw_set(username, password)
    mqtt_client.connect(mqttBroker, port=port)
    mqtt_client.loop_start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        mqtt_client.loop_start()
        
def main():
    global last_device_off
    while True:
        now = time.time()
        if now - last_device_off >= delay_device:
            print("Load off")
            GPIO.output(5, GPIO.LOW)
            time.sleep(300)
            last_device_off = time.time()
        else:
            with open("status.txt",'r') as f:
                status = f.read()
            if status == "True":
                GPIO.output(5, GPIO.HIGH)
                print("Load ON")
            elif status == "False":
                GPIO.output(5, GPIO.LOW)
                print("Load OFF")
        time.sleep(delay_main)

def internet():
    while True:
        GPIO.output(6, GPIO.HIGH)
        print("Internet is ON")
        time.sleep(3600)
        GPIO.output(6, GPIO.LOW)
        print("Internet is OFF")  
        time.sleep(3)

def compressor():
    while True:
        GPIO.output(23, GPIO.HIGH)
        print("Compressor is ON")
        time.sleep(1800)
        GPIO.output(23, GPIO.LOW)
        print("Compressor is OFF")
        time.sleep(1800)
def mail():
    time.sleep(15)
    while True:
        try:
            with open("status.txt",'r') as f:
                status = f.read()
            s = status
            print(s)
            email_user = "care.bariflolabs@gmail.com"
            email_password = "ifln keco pdbc hqts"
            # email_send = "data.bariflolabs@gmail.com"
            email_send = "gandupallihemanth86@gmail.com"
            #email_send = "g"
            subject = "IWMS Status"

            msg = MIMEMultipart()
            msg["From"] = email_user
            msg["To"] = email_send
            msg["Subject"] = subject
            if  s == "True":
                with open('data.json', 'r') as file:
                    data = json.load(file)
                sensor1 = round(data["sensor1"],2)
                sensor2 = round(data["sensor2"],2)
                sensor3 = round(data["sensor3"],2) 
                sensor4 = round(data["sensor4"],2)
                x = round(data["x"],2)
                y = round(data["y"],2)
                z = round(data["z"],2)
                print("t")
                #body = f"GW_Status:ON  Aeration:On  CompCurrVal:{current1} Amp  AerationCurrVal:{current2} Amp"
                body = f"GW_Status:ON  Aeration:On  sensor1 :{sensor1} Amp\nsensor2 :{sensor2} Amp\nsensor3 :{sensor3} Amp\nsensor4 :{sensor4} Amp\nX :{x} Amp\nY :{y} Amp\nZ :{z} Amp"
            else:
                print("f")
                body = "GW_status:ON Aeration Device :OFF"


            msg.attach(MIMEText(body,"plain"))

            text = msg.as_string()
            server = smtplib.SMTP("smtp.gmail.com",587)
            server.starttls()
            server.login(email_user,email_password)


            server.sendmail(email_user,email_send,text)
            server.quit()
            delay_mail = 5
            time.sleep(1800)
            
        except Exception as e:
            print(e)

if __name__ == '__main__':
    status = None
    time.sleep(15)
    threading.Thread(target=post_data_to_publish).start()
    threading.Thread(target=data_subscribe).start()
    threading.Thread(target=main).start()
    threading.Thread(target=internet).start()
    threading.Thread(target=compressor).start()
    threading.Thread(target=mail).start()
