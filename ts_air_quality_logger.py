from sds011 import *
from datetime import datetime
import time
import aqi
import json
import paho.mqtt.publish as publish
import paho.mqtt.client as paho
import psutil
import requests

def time_now():
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S)")
    return timestampStr

# Converting datetime object to string
dateTimeObj = datetime.now()
timestamp = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S)")
print('Current Timestamp : ', timestamp)

sensor = SDS011("/dev/ttyUSB0", use_query_mode=True )
url = 'http://api.openweathermap.org/data/2.5/weather?q=Willemstad,cw&appid=c3acae939fd8036cded481473b465156&units=metric'
        
def get_data(n=3):
       # sensor.sleep(sleep=False)
        pmt_2_5 = 0
        pmt_10 = 0
        time.sleep(10)
        for i in range (n):
            x = sensor.query()
            pmt_2_5 = pmt_2_5 + x[0]
            pmt_10 = pmt_10 + x[1]
            time.sleep(2)
            print("Measured")
        pmt_2_5 = round(pmt_2_5/n, 1)
        pmt_10 = round(pmt_10/n, 1)
       # sensor.sleep(sleep=True)
        time.sleep(2)
        return pmt_2_5, pmt_10
    
def conv_aqi(pmt_2_5, pmt_10):
    aqi_2_5 = aqi.to_iaqi(aqi.POLLUTANT_PM25, str(pmt_2_5))
    aqi_10 = aqi.to_iaqi(aqi.POLLUTANT_PM10, str(pmt_10))
    return aqi_2_5, aqi_10

def save_log():        
    with open("/home/pi/Sensor/air_quality.csv", "a") as log:
        dt = datetime.now()
        log.write("{},{},{},{},{}\n".format(dt, pmt_2_5, aqi_2_5, pmt_10, aqi_10))
    log.close()  

broker = "192.168.11.124"
port=1883

topic= "sensors"
topic2= "weatherTest"


def on_publish(client, userdata, result):
  print("published data is : ","pm2.5 -> " + int(pmt_2_5)+ " aqi2.5-> " + int(aqi_2_5)+ " pm10.0-> " + int(pmt_10)+ " aqi10.0-> " + int(aqi_10))
  pass

client1=paho.Client("controll")
client1.on_publish = on_publish
client1.connect(broker,port,keepalive=60)
          
while True: 
    pmt_2_5, pmt_10 = get_data()
    aqi_2_5, aqi_10 = conv_aqi(pmt_2_5, pmt_10)
 
    #Lat+Long+name of the first measuring station
    latitude = 12.127857
    longitude = -68.903840
    stationName = "BP Office"

    send_msg = {
            'name' : stationName ,
            'latitude': latitude  ,
            'longitude': longitude ,
            'PM2.5': pmt_2_5,
            'AQI2.5': int(aqi_2_5),
            'PM10': pmt_10,
            'AQI10': int(aqi_10)
        }

    res = requests.get(url)
    data = res.json()

    temp_feels = data['main']['feels_like']
    temp = data['main']['temp']
    temp_max = data['main']['temp_max']
    temp_min = data['main']['temp_min']
    humidity = data['main']['humidity']
    sunrise = data['sys']['sunrise']
    sunset = data['sys']['sunset']
    wind_deg = data['wind']['deg']
    wind_spd= data['wind']['speed']
    clouds = data['clouds']['all']
    
    json_msg = {
            'temp_feels':temp_feels,
            'temp':temp,
            'temp_max':temp_max,
            'temp_min':temp_min,
            'humidity':humidity,
            'sunrise':sunrise,
            'sunset':sunset,
            'wind_deg':wind_deg,
            'wind_spd':wind_spd,
            'clouds':clouds
          }

    try:
        print("Publishing payload:")
        print(send_msg)
        print(json_msg)
        client1.publish(topic, json.dumps(send_msg), qos=0, retain=False)
        client1.publish(topic2, json.dumps(json_msg), qos=0, retain=False)
        print("Saving log")
        save_log()
        print("Going to sleep")
        time.sleep(1)
    except:
        print ("[INFO] Failure in sending data") 
        time.sleep(12)
