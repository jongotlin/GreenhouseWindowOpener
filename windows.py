import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

openPower = 4
openGround = 17
closePower = 22
closeGround = 27
actuatorDuration = 2
threshold = 20

#todo...
temperature = 16

GPIO.setup(openPower, GPIO.OUT)
GPIO.setup(openGround, GPIO.OUT)
GPIO.setup(closePower, GPIO.OUT)
GPIO.setup(closeGround, GPIO.OUT)

def openWindow():
    if isOpen():
        print "return (already open)"
        return
    print "Opening"
    activate(openPower, openGround, "opening", "open")
    print "Opened"

def closeWindow():
    if isClosed():
        print "return (already closed)"
        return
    print "Closing"
    activate(closePower, closeGround, "closing", "closed")
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

if temperature >= threshold:
    openWindow()
else:
    closeWindow()
