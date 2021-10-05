import network
import socket
import machine
import ntptime
import time
import LM75
#mport mpu6050
import Render


# connect to wifi router
sta_if = network.WLAN(network.STA_IF)

if not sta_if.isconnected():
    print('connecting to network...')
    sta_if.active(True)
    sta_if.connect('DS', 'SputnikulOn4Antenni')
    while not sta_if.isconnected():
        time.sleep(0.3)
        print(".", end=" ")

print("")
print('network config:', sta_if.ifconfig())

# create a socket and listener for art-Net packages
# https://github.com/jsbronder/asyncio-dgram

#i2c 
i2c = machine.SoftI2C(scl=machine.Pin(22), sda=machine.Pin(23))



# imu 104 dec
# print(str(i2c.readfrom_mem(104,0x75,1)))
# imu = mpu6050.MPU6050(i2c)


# LED output RGBW
Output = Render.Render(i2cInterface=i2c)

# fan @ pin(0)
fan = machine.PWM(machine.Pin(0),duty=1023)

# Input Voltage sensor 1:7.81
inputVoltage = machine.ADC(machine.Pin(32))
inputVoltage.atten(machine.ADC.ATTN_11DB)

# enable outputs
enableAll = machine.Pin(27, machine.Pin.OUT, value=1)




# redComp
def calcRedcomp(self):
    pos = int(getTemp()*10)+300

redComp = machine.Timer(-1)


# NTP
print(str(time.localtime()))
ntptime.settime()
print(str(time.localtime()))
