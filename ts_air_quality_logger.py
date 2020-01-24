from sds011 import *
from datetime import datetime
import time
import aqi
import paho.mqtt.publish as publish
import psutil

def time_now():
    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S)")
    return timestampStr

# Converting datetime object to string
dateTimeObj = datetime.now()
timestamp = dateTimeObj.strftime("%d-%b-%Y (%H:%M:%S)")
print('Current Timestamp : ', timestamp)

sensor = SDS011("COM4", use_query_mode=True )
        
#time.sleep(10)
#pmt_2_5, pmt_10 = sensor.query()
#print (time_now(), end='')
#print(f"    PMT2.5: {pmt_2_5} μg/m3    ", end='')
#print(f"PMT10 : {pmt_10} μg/m3")
#time.sleep(2)

#aqi_2_5 = aqi.to_iaqi(aqi.POLLUTANT_PM25, str(pmt_2_5))
#aqi_10 = aqi.to_iaqi(aqi.POLLUTANT_PM10, str(pmt_10))

#print (time_now(), end='')
#print(f"    AQI (PMT2.5): {aqi_2_5}    ", end='')
#print(f"AQI(PMT10) : {aqi_10}")

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
            print("check")
        pmt_2_5 = round(pmt_2_5/n, 1)
        pmt_10 = round(pmt_10/n, 1)
        print("check2")
       # sensor.sleep(sleep=True)
        time.sleep(2)
        return pmt_2_5, pmt_10

#for i in range (5):
#    print (i, get_data())
    
def conv_aqi(pmt_2_5, pmt_10):
    aqi_2_5 = aqi.to_iaqi(aqi.POLLUTANT_PM25, str(pmt_2_5))
    aqi_10 = aqi.to_iaqi(aqi.POLLUTANT_PM10, str(pmt_10))
    return aqi_2_5, aqi_10

#pmt_2_5, pmt_10 = get_data()
#aqi_2_5, aqi_10 = conv_aqi(pmt_2_5, pmt_10)
#print (time_now(), end='')
#print(f"   PMT2.5: {pmt_2_5}μg/m3 (AQI:{aqi_2_5})  ", end='')
#print(f"PMT10: {pmt_10}μg/m3 (AQI:{aqi_10})")

def save_log():        
    with open("/Users/dyon.jacobs/Desktop/Sensor/air_quality.csv", "a") as log:
        dt = datetime.now()
        print("Date Time:",dt,
               "PMT 2.5:", pmt_2_5,
               "AQI 2.5:", aqi_2_5,
               "PMT 10:", pmt_10,
              "AQI 10:",aqi_10)
        log.write("{},{},{},{},{}\n".format(dt, pmt_2_5, aqi_2_5, pmt_10, aqi_10))
    log.close()  

#
#def on_connect(client, userdata, flags, rc):
#    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
#    client.subscribe(channelSubs)

#channelID = "962006"
#apiKey = "9MCNJW57WF27NTQL"
#topic = "channels/" + channelID + "/publish/" + apiKey
#mqttHost = "mqtt.thingspeak.com"

while True: 
    pmt_2_5, pmt_10 = get_data()
    aqi_2_5, aqi_10 = conv_aqi(pmt_2_5, pmt_10)
    print("Creating payload")
    tPayload = "field1=" + str(pmt_2_5)+ "&field2=" + str(aqi_2_5)+ "&field3=" + str(pmt_10)+ "&field4=" + str(aqi_10)
    try:
        print("Publishing payload:")
        print(tPayload)
        print("Saving log")
        save_log()
        print("Going to sleep")
        time.sleep(10)
    except:
        print ("[INFO] Failure in sending data") 
        time.sleep(12)
