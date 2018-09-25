import dht11
import smtplib
import time
from threading import Thread
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, render_template, redirect
from RPi import GPIO
from gpiozero import LightSensor, Buzzer

app = Flask(__name__)

LASER_PIN = 10
ldr = LightSensor(12)
buzzer = Buzzer(4)

on = '#2FD22F'
off = '#D22F2F'

# Each status will change color based on if it's on or off.
# It also gives more visual info to the user.
security = off
temp_threshold = 81  # change this to whatever you want
temperature = off
warning = False
toaddr = input('Enter your email: ')


def security():
    global security, ldr, buzzer, on, off
    while True:
        time.sleep(0.1)  # Do NOT remove.
        while security == on:
            time.sleep(0.1)  # Makes sure it doesn't murder the computer at night.
            if ldr.value < 0.900:
                print("Email sending...")
                print(ldr.value)
                send_email('Laser Activity', "Your laser has been tripped at {}".format(datetime.now().strftime('%b %d, %Y at %H:%M:%S %p')))
                buzzer.beep(0.5, 0.5, 8)
                time.sleep(8)
            else:
                buzzer.off()


def send_email(subject, text):
    msg = MIMEMultipart()
    msg['From'] = 'MakerUnfaire@gmail.com'
    msg['To'] = toaddr
    msg['Subject'] = subject
    msg.attach(MIMEText(text, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(msg['From'], 'feoelyrgclsbhsns')  # don't abuse pls
    text = msg.as_string()
    server.sendmail(msg['From'], toaddr, text)
    server.quit()

    print("Email Sent:\n" + text)


def c_to_f(temp):
    '''Converts a temperature in Celsius to Fahrenheit.'''
    return int(temp) * 1.8 + 32


@app.route('/')
def home():
    global security, temp_threshold, temperature, on, off, to_addr, warning

    sensor = dht11.DHT11(pin=14)
    result = sensor.read()
    while not result.is_valid():
        result = sensor.read()

    if result.is_valid():
        temp = '{0:.1f}°F'.format(c_to_f(result.temperature))
    else:
        temp = 'Error'

    if temperature == off:
        temp = ''
    hr = datetime.now().strftime('%b %d, %Y at %H:%M:%S %p')

    if c_to_f(result.temperature) > temp_threshold and not warning:
        send_email('Temperature', 'Alert: Temperature is above 81 F')
        warning = True
    elif c_to_f(result.temperature) <= temp_threshold and warning and result.temperature != 0:
        send_email('Temperature', 'Alert: Temperature is below 81 F')
        warning = False

    return render_template('index.html', temp=temp, timestamp=hr, security=security, temperature=temperature, purple="#997AF8")


@app.route('/camera/')
def camera():
    return redirect('http://127.0.0.1:8000/index.html', code=302)  # Redirect to other RPi


@app.route("/sectoggle/", methods=['POST'])
def sectoggle():
    global security
    security = on if security == off else off
    return redirect("http://127.0.0.1:5000/", code=302)


@app.route("/temtoggle/", methods=['POST'])
def temtoggle():
    global temperature
    temperature = on if temperature == off else off
    return redirect("http://127.0.0.1:5000/", code=302)


if __name__ == '__main__':
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(LASER_PIN, GPIO.OUT)

    # GPIO.cleanup()

    # loop = asyncio.get_event_loop()
    # loop.create_task(security())
    print("Starting security...")
    securitythread = Thread(target=security)
    securitythread.setDaemon(True)
    securitythread.start()
    print("Security started.")
    print("App started...")
    app.run(host='127.0.0.1')
    print("App ended.")
