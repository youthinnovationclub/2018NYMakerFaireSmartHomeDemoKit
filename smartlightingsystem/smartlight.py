# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.

from neopixel import *
import RPi.GPIO as GPIO
import argparse
import signal
import sys
import time

LDR_PIN = 12

def rc_time(pin):
	count = 0

	GPIO.setup(pin, GPIO.OUT)
	GPIO.output(pin, GPIO.LOW)
	time.sleep(0.1)

	GPIO.setup(pin, GPIO.IN)

	while(GPIO.input(pin) == GPIO.LOW):
		count += 1
	return count

def signal_handler(signal, frame):
	colorWipe(strip, Color(0,0,0))
	sys.exit(0)

def opt_parse():
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', action='store_true', help='clear the display on exit')
	args = parser.parse_args()
	if args.c:
		signal.signal(signal.SIGINT, signal_handler)

# LED strip configuration:
LED_COUNT      = 16      # Number of LED pixels.
LED_PIN        = 13      # GPIO pin connected to the pixels (12, 18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 1       # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
	"""Wipe color across display a pixel at a time."""
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
		strip.show()
		time.sleep(wait_ms/1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=10):
	"""Movie theater light style chaser animation."""
	for j in range(iterations):
		for q in range(3):
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, color)
			strip.show()
			time.sleep(wait_ms/1000.0)
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, 0)
				
def wheel(pos):
	"""Generate rainbow colors across 0-255 positions."""
	if pos < 85:
		return Color(pos * 3, 255 - pos * 3, 0)
	elif pos < 170:
		pos -= 85
		return Color(255 - pos * 3, 0, pos * 3)
	else:
		pos -= 170
		return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
	"""Draw rainbow that fades across all pixels at once."""
	for j in range(256*iterations):
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, wheel((i+j) & 255))
		strip.show()
		time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
	"""Draw rainbow that uniformly distributes itself across all pixels."""
	for j in range(256*iterations):
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
		strip.show()
		time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
	"""Rainbow movie theater light style chaser animation."""
	for j in range(256):
		for q in range(3):
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, wheel((i+j) % 255))
			strip.show()
			time.sleep(wait_ms/1000.0)
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, 0)
				
def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)

# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    opt_parse()
    
    setup()
    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    print ('Press Ctrl-C to quit.')
    cloop=1
    while True:
        brightness = rc_time(LDR_PIN)
        print(brightness)
        if brightness < 100:
			print("super bright ", brightness)
			theaterChase(strip, Color(127, 127, 127))  # White theater chase
			colorWipe(strip, Color(0, 0, 0))  # no light
			time.sleep(1)
		elif brightness < 1000:
			print("bright ", brightness)
			theaterChase(strip, Color((127,   0,   0))  # Red theater chase
			colorWipe(strip, Color(50, 50, 50))  # dim
			time.sleep(1)
		elif brightness < 2000:
			print("dark ", brightness)
			theaterChase(strip, Color(  0,   0, 127))  # Blue theater chase
			colorWipe(strip, Color(150, 150, 150))  # bright LED
			time.sleep(1)
        else:
			print("very dark ", brightness)
			colorWipe(strip, Color(255, 255, 255))  # full light on
			time.sleep(1)
