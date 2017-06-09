import RPi.GPIO as GPIO
import time
import os
import glob
import requests

url = 'http://vaxthus.gotlin.se/api/event'
apiUser = 'api'
apiPassword = '***'

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

openPower = 22
openGround = 27
closePower = 23
closeGround = 17

actuatorDuration = 60 + 60 + 25 + 30 # 30 extra seconds
threshold = 20

os.system('modprobe w1-gpio') 
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folders = glob.glob(base_dir + '28*') 
device_files = [device_folders[0] + '/w1_slave', device_folders[1] + '/w1_slave']
 
def read_temp_raw(sensor):
    f = open(device_files[sensor], 'r') 
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp(sensor):
    lines = read_temp_raw(sensor)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw() 
    equals_pos = lines[1].find('t=') 
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:] 
        temp_c = float(temp_string) / 1000.0
        return temp_c

GPIO.setup(openPower, GPIO.OUT)
GPIO.setup(openGround, GPIO.OUT)
GPIO.setup(closePower, GPIO.OUT)
GPIO.setup(closeGround, GPIO.OUT)

def openWindow():
    if isOpen():
        print "return (already open) (", read_temp(1), " degrees)"
        return
    print "Opening (", read_temp(1), " degrees)"
    activate(openPower, openGround, "opening", "open")
    payload = {'event': 'open-window'}
    response = requests.post(url, data=payload, headers=[], auth=(apiUser, apiPassword))
    if response.status_code == 204:
        print 'OK'
    else:
        print 'FAIL', response.status_code, response.content
    print "Opened"

def closeWindow():
    if isClosed():
        print "return (already closed) (", read_temp(1), " degrees)"
        return
    print "Closing (", read_temp(1), " degrees)"
    activate(closePower, closeGround, "closing", "closed")
    payload = {'event': 'close-window'}
    response = requests.post(url, data=payload, headers=[], auth=(apiUser, apiPassword))
    if response.status_code == 204:
        print 'OK'
    else:
        print 'FAIL', response.status_code, response.content
    print "Closed"

def activate(power, ground, statePre, statePost):
    if inAction():
        return
    writeToFile(statePre)
    GPIO.output(power, GPIO.HIGH)
    GPIO.output(ground, GPIO.HIGH)
    time.sleep(actuatorDuration)
    GPIO.output(power, GPIO.LOW)
    GPIO.output(ground, GPIO.LOW)
    writeToFile(statePost)

def writeToFile(state):
    file = open("window-state.txt", "w")
    file.write(state)
    file.close()
    
def inAction():
    state = open("window-state.txt", "r").read()
    return state == "opening" or state == "closing"

def isOpen():
    state = open("window-state.txt", "r").read()
    return state == "opening" or state == "open"

def isClosed():
    state = open("window-state.txt", "r").read()
    return state == "closing" or state == "closed"

temperature = read_temp(1)
if temperature >= threshold:
    openWindow()
else:
    closeWindow()
