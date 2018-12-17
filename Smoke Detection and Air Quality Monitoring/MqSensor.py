import requests
from time import sleep
import math
#import time
#import Adafruit library for ADS1115 ADC
import Adafruit_ADS1x15

from twilio.rest import Client

account_sid = '' # Found on Twilio Console Dashboard
auth_token = '' # Found on Twilio Console Dashboard

myPhone = '' # Phone number you used to verify your Twilio account
TwilioNumber = '' # Phone number given to you by Twilio

client = Client(account_sid, auth_token)

#Create an ADS1115 instance
adc=Adafruit_ADS1x15.ADS1115()
LR = 5 #adjustable load resistance in kilo ohms

#Enter Your API key here
APIKey=""
#ThinSpeak API URL
URL='https://api.thingspeak.com/update?api_key=%s' % APIKey
#smoke
APIKey2 = ""
URL2='https://api.thingspeak.com/update?api_key=%s' % APIKey2
#Carbon dioxide
APIKey3 = ""
URL3='https://api.thingspeak.com/update?api_key=%s' % APIKey3

#take 2 points from the curve in the data sheet
#take the point P1 (x1 = 200, y1 = ~ 1.62) and P2 (x2 = 10000, y2 = ~ 0.26). 

class MqSensor:

  def __init__(self, Rs_Clean_Air, y2, y1, x2, x1, sensorType):

    self.Rs_Clean_Air = Rs_Clean_Air #from the data sheet 
    self.y2 = y2
    self.y1 = y1
    self.x2 = x2
    self.x1 = x1
    self.sensorType = sensorType
    
  def setup(self, channel):
    global c  #y intercept
    global m  #slope
    global RO #sensor resistance in known concetration or in fresh air

    #calculate slope
    m = ( math.log10(self.y2) -  math.log10(self.y1) ) / ( math.log10(self.x2) - math.log10(self.x1) )

    print ("slopefor {0} is {1}".format(self.sensorType,m))
    #calculate the y intercept c from linear equation
    c = math.log10 (self.y1) - m*math.log10(self.x1)
    
    numReadings = 10
    sensorReading  = 0
   

    print ("{0} sensor calibrating....".format(self.sensorType))
    for x in range(numReadings):
     sensorReading = sensorReading + adc.read_adc(channel, gain=2/3);
     sleep(1)
    sensorReading = sensorReading/numReadings; #average sensor value
    sensorVoltage = ((sensorReading *6.144)/32767)
    #The sensor and the load resistor forms a voltage divider, LR, 5V Vc, we can calculate the resistance of sensor
    RS = LR*((5-sensorVoltage)/sensorVoltage); #Sensing resistance at various gas concentration
    RO = RS/self.Rs_Clean_Air; #Clean airResistance = RS/R0 --  from datasheet
    
  def calculateppm(self,channel): 
    voltage = (adc.read_adc(channel, gain =2/3)*6.144/32767)
    RS_gas = LR*((5-voltage)/voltage)
    ppmRatio = RS_gas/RO
    ppm_log = (math.log10(ppmRatio)-c)/m
    ppm = pow(10, ppm_log)
    #sleep(1)
    return ppm	



if __name__ == '__main__':
 #MQ 7 Carbon Monoxide Sensor: points from data sheet in this order: y2, y1, x2, x1	
 #mq7_CO = MqSensor(28, 0.22, 1.8, 1000, 50, "mq7_CO" )
 #mq7_CO.setup(0) #include ADS channel used as parameter
 


 #MQ 2 Sensor: points from data sheet in this order:Rs_Clean_Air, y2, y1, x2, x1

 #mq2_Smoke = MqSensor(9.8, 0.6, 3.3, 10000, 200, "mq2_Smoke" )
 #mq2_Smoke.setup(0)
 
 mq135_CO2 = MqSensor(3.7, 1.2, 2.3, 100, 10, "mq135_CO2" )
 mq135_CO2.setup(0)
 
 
 

 
 
 while True:
     #try: 
 	#We will need to include the channel parameter in the function if we have connected several sensors
          ppm_CO = mq7_CO.calculateppm(0) #ads channel
          print 'carbon monoxide ppm', ppm_CO
          Visualization on Thingsspeak 
          connection=requests.post(URL+'&field1=%.2f'%(ppm_CO))
          
          Twilio Notification
          if (ppm_CO > 5):
              print "sending notification"
              client.messages.create(
                  to=myPhone,
                  from_=TwilioNumber,
                  body='Sensor Alert: MQ7 - Carbon monoxide levels exceeded the threshold')
  	       
  	  #ppm_smoke = mq2_Smoke.calculateppm(0)

          #print 'Smoke ppm', ppm_smoke
          #connection=requests.post(URL2+'&field1=%.2f'%(ppm_smoke))
                    #Twilio Notification
          #if (ppm_smoke > 1000):
           #   print "sending notification"
            #  client.messages.create(
             #     to=myPhone,
              #    from_=TwilioNumber,
               #   body='Sensor Alert: MQ2 - Smoke levels exceeded the threshold')
           
      
          #print 'Smoke ppm', ppm_smoke
          #connection=requests.post(URL2+'&field1=%.2f'%(ppm_smoke))


          ppm_CO2 = mq135_CO2.calculateppm(0)
          print 'CO2 ppm', ppm_CO2
          connection=requests.post(URL3+'&field1=%.2f'%(ppm_CO2))

          

          #MQ 135 Sensor: points from data sheet in this order: y2, y1, x2, x1
          sleep(1)
          
     #except:
      #    print ('Erro occured')
       #   break



	



     




