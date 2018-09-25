import sys
import smbus
import time
import dht11
import RPi.GPIO as GPIO

mode=GPIO.getmode()

Forward=26
Backward=20
sleeptime=1
TEMP_SENSOR = 14

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Forward, GPIO.OUT)
    GPIO.setup(Backward, GPIO.OUT)

def forward(x):
    GPIO.output(Forward, GPIO.HIGH)
    print("Moving Forward")
    time.sleep(x)
    GPIO.output(Forward, GPIO.LOW)

def reverse(x):
    GPIO.output(Backward, GPIO.HIGH)
    print("Moving Backward")
    time.sleep(x)
    GPIO.output(Backward, GPIO.LOW)

def main():
    sensor_instance = dht11.DHT11(pin = TEMP_SENSOR)
    initTemp = sensor_instance.read().temperature
    print("initial room temperature ", initTemp)
    while True:
        result = sensor_instance.read()
        if result.is_valid():
            print("temperature ", result.temperature)
            if int(result.temperature) > (initTemp + 1):
                print("start AC")
                i = 0
                while i < 2:
                    forward(5)
                    reverse(5)
                    i = i + 1
                
if __name__ == '__main__':
    try:
        setup()
        main()
    finally:
        GPIO.cleanup()
