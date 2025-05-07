
#  if you want to run code, make sure to run it through thonny!!








############################################################
#################### IMPORT LIBRARIES ######################
############################################################
from time import sleep                     # <<< DO NOT REMOVE >>>
from picozero import RGBLED
import time
import machine
import onewire
import ds18x20
from mfrc522 import MFRC522
from machine import Pin, ADC, I2C
from ssd1306 import SSD1306_I2C


# Imports for MQTT communication           # <<< DO NOT REMOVE >>>
try:
    import network                         # <<< DO NOT REMOVE >>>
except ImportError:
    print("Error: 'network' module not found. Ensure you are using a compatible MicroPython environment.")
import json                                # <<< DO NOT REMOVE >>>
from umqtt.robust import MQTTClient        # <<< DO NOT REMOVE >>>



############################################################
################# SPECIFY PINS AND OBJECTS #################
############################################################
LED = RGBLED(red = 18, green = 19, blue = 20, active_high = True)

# Temperature sensor info
PinNum = machine.Pin(28)
tempSensor = ds18x20.DS18X20(onewire.OneWire(PinNum))
tempList = tempSensor.scan()

#RFID reader info
reader = MFRC522(spi_id=0,sck=6,miso=4,mosi=7,cs=5,rst=8)

#OLED Screen info
display_width = 128 # pixel x values = 0 to 127
display_height = 64 # pixel y values = 0 to 63
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000) # TX pin is Pin 0, RX pin is Pin 1
display = SSD1306_I2C(display_width, display_height, i2c)

############################################################
##################### OTHER SETUP STUFF ####################
############################################################

# Wi-Fi and MQTT settings
SSID = "WilfongEngr301" # Raspberry Pi 4 Wi-Fi name                               # <<< DO NOT REMOVE >>>
PASSWORD = "BoilerUp" # Raspberry Pi 4 Wi-Fi password, WPA/WPA2 security          # <<< DO NOT REMOVE >>>
MQTT_BROKER = "10.42.0.1"  # Raspberry Pi 4's IP                                  # <<< DO NOT REMOVE >>>
TOPIC = "pico/data" # "pico/data" is just a label                                 # <<< DO NOT REMOVE >>>
                    # It helps organize messages, like folders in a file system.  # <<< DO NOT REMOVE >>>
                    # The TOPIC could be any string, but leave it as "pico/data"  # <<< DO NOT REMOVE >>>

SENSOR_ID = "Team04"  # !!!-- CHANGE THIS AS DIRECTED BY DR. WILFONG --!!!

# Connect to Wi-Fi                                      # <<< DO NOT REMOVE >>>
wlan = network.WLAN(network.STA_IF)                     # <<< DO NOT REMOVE >>>
wlan.active(True)                                       # <<< DO NOT REMOVE >>>
wlan.connect(SSID, PASSWORD)                            # <<< DO NOT REMOVE >>>

LED.color = (0,0,255)
while not wlan.isconnected():                           # <<< DO NOT REMOVE >>>
    pass                                                # <<< DO NOT REMOVE >>>

sleep(2)  # Extra delay for stability                   # <<< DO NOT REMOVE >>>
LED.color = (0,255,0)

# Optional: disable Wi-Fi power save                    # <<< DO NOT REMOVE >>>
wlan.config(pm = 0xa11140)                              # <<< DO NOT REMOVE >>>

# Connect to MQTT broker with reconnect support         # <<< DO NOT REMOVE >>>
client = MQTTClient(f"client_{SENSOR_ID}", MQTT_BROKER) # <<< DO NOT REMOVE >>>
client.DEBUG = True                                     # <<< DO NOT REMOVE >>>

# Try to connect to MQTT broker                         # <<< DO NOT REMOVE >>>
try:                                                    # <<< DO NOT REMOVE >>>
    client.connect()                                    # <<< DO NOT REMOVE >>>
    print("Connected to MQTT broker!")
    LED.color = (0,255,0)
except Exception as e:                                  # <<< DO NOT REMOVE >>>
    print("Failed to connect to MQTT broker:", e)
    LED.color = (255,0,0)


############################################################
####################### INFINITE LOOP ######################
############################################################
while True:
    
    
    
    tempSensor.convert_temp()
    time.sleep_ms(750)
    for tsListItem in tempList:
        tempC = tempSensor.read_temp(tsListItem)
        tempF = tempC * (9/5) + 32
        x = print("{:.2f}".format(tempC), '[degC]')
        
    display.fill(0) # clears display
    display.text("Currently locked", 0, 0) # write text starting at x=0 and y=0
    display.show()
    sleep(1)
        
    reader.init()
    (stat, tag_type) = reader.request(reader.REQIDL)
    if stat == reader.OK:
        (stat, uid) = reader.SelectTagSN()
        if stat == reader.OK:
            card = int.from_bytes(bytes(uid),"little",False)
            if card == 450427139:
                print("Card ID: "+ str(card)+" UNLOCKED")
                time.sleep(1)
                display.fill(0)
                for x in range(60): 

                    display.text("Temperature is:", 0, 0) # write text starting at x=0 and y=0
                    display.text(str(tempC), 0, 40)
                    display.show() # make the changes take effect
                
                display.fill(0) # clears display
            else:
                print("Card ID: "+ str(card)+" UNKNOWN CARD!")
                display.fill(0) # clears display
                display.text("Currently locked", 0, 0) # write text starting at x=0 and y=0
                display.show()
                time.sleep(1)

    
    # Create and send MQTT payload                               # <<< DO NOT REMOVE >>>
    message_data = {                                             # <<< DO NOT REMOVE >>>
        "sensorID": SENSOR_ID,                                   # <<< DO NOT REMOVE >>>
        "temperatureReading": tempC                              # <<< DO NOT REMOVE >>>
    }                                                            # <<< DO NOT REMOVE >>>
    message_json = json.dumps(message_data)  # Convert to JSON   # <<< DO NOT REMOVE >>>
    
    # Try to publish message to MQTT broker                                   # <<< DO NOT REMOVE >>>
    try:                                                                      # <<< DO NOT REMOVE >>>
        client.publish(TOPIC, message_json, retain=True) # Send MQTT payload  # <<< DO NOT REMOVE >>>
    
        # Print MQTT payload to Thonny's terminal/shell/console
        print(f"Published: {message_json}")
    except Exception as e:                                                    # <<< DO NOT REMOVE >>>
        print("Publish failed:",e)
        LED.color = (255,0,0)
    
    # Determines how often the MQTT payload (i.e., sensorID and temperature reading) is sent
    sleep(2)
