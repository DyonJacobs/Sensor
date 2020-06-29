from sds011 import *
from datetime import datetime
import time
import aqi
import json
import paho.mqtt.publish as publish
import paho.mqtt.client as paho
import psutil
import requests

#Acquire the current time
def time_now():
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S)")
    return timestampStr

# Converting datetime object to string
dateTimeObj = datetime.now()
timestamp = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S)")
print('Current Timestamp : ', timestamp)

#Here the sensor object is established, the 'ttyUSB0' is the result from
#the port_check.py showing in which USB port the Sensor currently is.
sensor = SDS011("/dev/ttyUSB0", use_query_mode=True )

#The URL of Openweathermap, used to acquire weather data.
url = 'http://api.openweathermap.org/data/2.5/weather?q=Willemstad,cw&appid=c3acae939fd8036cded481473b465156&units=metric'

#three different air quality measurements are done in a 2 second interval,
#the average result of these three test is returned. 
def get_data(n=3):
       # sensor.sleep(sleep=False)
        pmt_2_5 = 0
        pmt_10 = 0
        time.sleep(2)
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

#Convert the PM values to AQI values.    
def conv_aqi(pmt_2_5, pmt_10):
    aqi_2_5 = aqi.to_iaqi(aqi.POLLUTANT_PM25, str(pmt_2_5))
    aqi_10 = aqi.to_iaqi(aqi.POLLUTANT_PM10, str(pmt_10))
    return aqi_2_5, aqi_10

#Save the data in a csv file locally on the Raspberry Pi
def save_log():        
    with open("/home/pi/Sensor/air_quality.csv", "a") as log:
        dt = datetime.now()
        log.write("{},{},{},{},{}\n".format(dt, pmt_2_5, aqi_2_5, pmt_10, aqi_10))
    log.close()  

#This is where the data gets sent to, the server with the broker running.
#The IP Address is the virtual IP Address set-up for this project on the
#BearingPoint Caribbean server
broker = "192.168.0.130"
port=1883

#MQTT topics to send the data to, the data can be requested from the broker
#by subscribing to these topics.
topic= "sensors"
topic2= "weatherTest"

# Print the measured values
def on_publish(client, userdata, result):
  print("published data is : ","pm2.5 -> " + int(pmt_2_5)+ " aqi2.5-> " + int(aqi_2_5)+ " pm10.0-> " + int(pmt_10)+ " aqi10.0-> " + int(aqi_10))
  pass

#Connect to the MQTT Broker Server and define the publish method.
client1=paho.Client("controll")
client1.on_publish = on_publish
client1.connect(broker,port,keepalive=60)

#While the script is running perform these actions.
while True:
#Acquire PM values in the air, run get_data method
    pmt_2_5, pmt_10 = get_data()
#Convert the PM values to AQI Values
    aqi_2_5, aqi_10 = conv_aqi(pmt_2_5, pmt_10)
#Get current time in y/m/d format
    ymd = time.strftime('%Y%m%d') 
    ymd = int(ymd)
#Lat+Long+name of the two measuring stations, hard-coded because no GPS
    latitude = 12.127857
    longitude = -68.903840
    latitude2 = 12.102685
    longitude2 = -68.929502
    station1 = "BP Office"
    station2 = 'Dyons Crib'
#Get current time in milliseconds
    millis_time = lambda: int(round(time.time() * 1000))  
    dateTimeObj = datetime.now()

    timestamp = dateTimeObj.strftime("%d/%m/%Y %H:%M:%S")
#   timestamp = dateTimeObj.strftime("%d-%m-%YT%H:%M:%S.%f-04:00")
#   timestamp = timestamp[:-3]

#Create JSON file, this one isn't send to the server, test message
    send_msg = {
            'name' : station1,
            'latitude' :latitude,
            'longitude' :longitude,
            'geo_location':'12.127857, -68.903840',
            'timestamp': timestamp ,
            'PM2.5': pmt_2_5,
            'AQI2.5': int(aqi_2_5),
            'PM10': pmt_10,
            'AQI10': int(aqi_10)
        }
          

#Acquire all data from the openweathermap url
    res = requests.get(url)
    data = res.json()

#Save the interesting data as variables
    temp_feels = data['main']['feels_like']
    temp = data['main']['temp']
    humidity = data['main']['humidity']
    sunrise = data['sys']['sunrise']
    sunset = data['sys']['sunset']
    wind_deg = data['wind']['deg']
    wind_spd= data['wind']['speed']
    clouds = data['clouds']['all']
    
    json_msg = {
            'temp_feels':temp_feels,
            'temp':temp,
            'humidity':humidity,
            'sunrise':sunrise,
            'sunset':sunset,
            'wind_deg':wind_deg,
            'wind_spd':wind_spd,
            'clouds':clouds
          }
#Json Message for first measuring station    
    test_msg = {
            'name' : station1,
            'latitude' :latitude,
            'longitude' :longitude,
            'geo_location':'12.127857, -68.903840',
            'timestamp': millis_time(),
            'id' : 1,
            'ymd' : ymd,
#            'timestamp': timestamp,
            'PM2.5': pmt_2_5,
            'AQI2.5': int(aqi_2_5),
            'PM10': pmt_10,
            'AQI10': int(aqi_10),
            'temp_feels':temp_feels,
            'temp':temp,
            'humidity':humidity,
            'sunrise':sunrise,
            'sunset':sunset,
            'wind_deg':wind_deg,
            'wind_spd':wind_spd,
            'clouds':clouds
      }
#Json message for second measuring station
    test_msg2 = {
            'name' : station2,
            'latitude' :latitude2,
            'longitude' :longitude2,
            'geo_location':'12.102679, -68.929496',
            'timestamp': millis_time(),
            'id' : 2,
            'ymd' : ymd,
#            'timestamp': timestamp,
            'PM2.5': pmt_2_5,
            'AQI2.5': int(aqi_2_5),
            'PM10': pmt_10,
            'AQI10': int(aqi_10),
            'temp_feels':temp_feels,
            'temp':temp,
            'humidity':humidity,
            'sunrise':sunrise,
            'sunset':sunset,
            'wind_deg':wind_deg,
            'wind_spd':wind_spd,
            'clouds':clouds
      }


#After the two JSON messages are created, they will be sent to the server
    try:
        print("Publishing payload:")
#        print(send_msg)
#        print(json_msg)
#Here the data is published to topic and topic2, no database is subcribed to them
#        client1.publish(topic, json.dumps(send_msg), qos=0, retain=False)
#        client1.publish(topic2, json.dumps(json_msg), qos=0, retain=False)

#Creating the test messages again in JSON format,
#Aribtrary (can be removed) but used during project to randomize the data to
#fill up the database engine.
        test_msg = {
            'name' : station1,
            'latitude' :latitude,
            'longitude' :longitude,
            'geo_location':'12.127857, -68.903840',
            'timestamp': millis_time(),
            'id' : 1,
            'ymd' : ymd,
#            'timestamp': timestamp,
            'PM2.5': pmt_2_5,
            'AQI2.5': int(aqi_2_5),
            'PM10': pmt_10,
            'AQI10': int(aqi_10),
            'temp_feels':temp_feels,
            'temp':temp,
            'humidity':humidity,
            'sunrise':sunrise,
            'sunset':sunset,
            'wind_deg':wind_deg,
            'wind_spd':wind_spd,
            'clouds':clouds
      }
        test_msg2 = {
            'name' : 'Dyons Crib',
            'latitude' :latitude2,
            'longitude' :longitude2,
            'geo_location':'12.102679, -68.929496',
            'timestamp': millis_time(),
            'id' : 2,
            'ymd' : ymd,
#            'timestamp': timestamp,
            'PM2.5': pmt_2_5,
            'AQI2.5': int(aqi_2_5),
            'PM10': pmt_10,
            'AQI10': int(aqi_10),
            'temp_feels':temp_feels,
            'temp':temp,
            'humidity':humidity,
            'sunrise':sunrise,
            'sunset':sunset,
            'wind_deg':wind_deg,
            'wind_spd':wind_spd,
            'clouds':clouds
      }
#Data is published to testTopic and testTopic2, broker on server is
#subscribed to these two topics
        client1.publish("testTopic", json.dumps(test_msg), qos=0, retain=False)
        client1.publish("testTopic2", json.dumps(test_msg2), qos=0, retain=False)
#Data is saved locally (on Pi) on csv file
        print("Saving log")
        save_log()
#Pause for 5 seconds before acquiring data again
        print("Going to sleep")
        time.sleep(5)
#When something goes wrong, sleep 12 seconds and try again.
    except:
        print ("[INFO] Failure in sending data") 
        time.sleep(12)
