import si7021   #import temperature and humidity sensor library (our GIVEN sensor)
import tsl2561  #import light sensor library ( our ADDITIONAL sensor ) 
import machine  #micropython esp8266
import json     #import json python library
import time     #import time library 
import network  #import network library 
from machine import I2C, Pin #connection to i2c pin of esp8266

#function for user mode selection ( for demo purposes )
def mode_selection():
        msg = "Thank you for using THL Sensor, your personal assistant!\n"
        msg+= "Please select one of the modes below:\n"
        msg+= "A: Baby Room Monitor\n"
        msg+= "B: Study Room Monitor\n"
        msg+= "C: Greenhouse Monitor\n"
        msg+= "D: Instruments Room Monitor\n"
        msg+= "E: Custom (Define your own threshold level)\n"
        print (msg)
        selection = input("Your mode: ").lower()
        if selection=='a':
                print("You have selected Mode A: Baby Room Monitor [Temperature: 20-22 C  Humidity: 50%]") 
        elif selection=='b':
                print("You have selected Mode B: Study Room Monitor [Temperature: 24-26 C  Light Intensity: 60-100lux]") 
        elif selection=='c':
                print("You have selected Mode C: Greenhouse Monitor [Temperature: 25-37 C  Humidity: 50-100%] Light Intensity: Custom]")
        elif selection=='d':
                print("You have selected Mode D: Instruments Room Monitor [Temperature: 23-25 C  Humidity: 20-50%] Light Intensity: 0-50]")
        elif selection=='e':
                print("You have selected Mode E: Custom ")
                custom_mode()
        else:
                print("Invalid mode")
                mode_selection()
#future work would be to sync selection with text messaging system(thingspeak and twilio) as demonstrated in demo

#function to read user input for Mode E: Custom 
def custom_mode():
        Threshold_Temp = input("Threshold Temperature: ")
        Threshold_RH = input("Threshold Humidity: ")
        Threshold_Light = input("Threshold Light Intensity: ")
        value = "You have selected:\n"
        value += "Threshold Temperature: " + str(Threshold_Temp) + " C\n"
        value += "Threshold Humidity: "+ str(Threshold_RH)+" %\n"
        value += "Threshold Light Intensity: " + str(Threshold_Light)+" lux\n"
        print(value)


        
i2c = I2C(scl=Pin(5),sda=Pin(4), freq=100000)   #address of the slave
thsensor = si7021.Si7021(i2c)                   #connect ESP8266 to temperature and humidity sensor
luxsensor = tsl2561.TSL2561(i2c)                #connect ESP8266 to light sensor

#connection to wifi
print('Connecting Wifi...')
ap_if = network.WLAN(network.AP_IF)
ap_if.active(False)

sta_if =network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Andy','12345678') #used our own hotspot  
while not sta_if.isconnected():
	pass
print('Wifi Connected')

#connection to MQTT ( thingspeak mqtt broker used here )
print('Connecting ThingSpeak...')
from umqtt.simple import MQTTClient
myMqttClient = 'stradivarius'  #our mqtt client name
thingspeakIoUrl = 'mqtt.thingspeak.com'
c = MQTTClient(myMqttClient, thingspeakIoUrl, 1883)
c.connect()
print ('ThingSpeak Connected')

thingspeakChannelId = "227294"  #Our thingspeak channel ID
thingspeakChannelWriteapi = "1JO35YU5EMY55E4B" #Our thingspeak Write API Key
publishPeriodInSec = 3 #publishing data on thingspeak every 3 seconds

mode_selection() #perform mode_selection function as defined above

#begin main here 
print ('Initialising sensors... ')
print ('Fetching data... ')

while True:
        #read sensors (readings already converted to appropriate units)
        temp = thsensor.readTemp()
        humidity = thsensor.readRH()
        lux = luxsensor.read()
        
        #readings in JSON format
        readings={
                "Temperature" :str(thsensor.readTemp()) +" C",
                "Humidity": str(thsensor.readRH()) +" %",
                "Light Intensity": str(luxsensor.read()) +" lux",
        }

        #publishing onto thingspeak MQTT
        credentials = "channels/{:s}/publish/{:s}".format(thingspeakChannelId, thingspeakChannelWriteapi)  
        payload = "field1={:.1f}&field2={:.1f}&field3={:.1f}\n".format(temp, humidity, lux)
        c.publish(credentials, payload) 
        time.sleep(publishPeriodInSec)
        
        #print readings in JSON format on terminal
        print(json.dumps(readings)) 
c.disconnect()



