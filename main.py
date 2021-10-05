import uasyncio as asyncio
import _thread
import time

val = [1023,0,0,0]
#0 # -> 5600K
brightnessRange =[1, .90, .80, .70, .60, .50, .40, .30, .20, .10, .75, .25, .09, .08, .07, .06, .05, .04, .03, .02, .01, 0.005, 0.002]
bId = 0

'''uLerp: intger interpolation for 10bit input and blend

uLerp is ultra simple interpolation, only by simplest archmetic for fas interpolation
'''
def uLerp(a:int, b:int, position:int):

    if a < 0 or b < 0 or position < 0:
        raise TypeError('all values must be positive numbers')
    if a > 1023 or b > 1023 or position > 1023:
        raise TypeError('values must be within range of 0-1023 ie. 10bit values')

    a += 1
    b += 1

    r1 = (1023 - position) * a
    r2 = position * b
    return (r1+r2)>>10 

'''setValues:

Helper function to set list of values in RGBW order and with floating point scaler
'''
def setValues(val, mult=1., debug=False):
    for i in range(4):
        finalInt = int(val[i]*mult)
        if debug:
            print("CH: "+str(i)+" Out: "+str(val)+" Real Out: "+str(finalInt))
        genPWM[i].duty(finalInt)

'''nextBrightness:

Helper function go through standard brightness to do manual measutrements
'''
def nextBrightness():
    global bId
    print("Current int: "+str(brightnessRange[bId]*100)+"%")
    setValues(val,brightnessRange[bId])
    if bId < len(brightnessRange):
        bId+=1
    else:
        bId=0

    print("Current temp: "+getTemp()+"C")

class ArtNetClient:
    '''Ultra simple Art-Net client 
    
    Ignore all cheks and just push 1st 4 values in 1st DMX universe onto the LEDs
    '''

    def __init__(self, renderer):
        self._render = renderer
        # TODO check if inet is up
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((sta_if.ifconfig()[0],6454))
        self._thread_id = _thread.get_ident()
        #self._sock.setblocking(False)

        _thread.start_new_thread(self.udpReader,())

    def udpReader(self): 
        while True:
            try:
                data, addr = self._socket.recvfrom(1024)
                # blend WB
                inputs = (data[18]*4,data[19]*4,data[20]*4)
                intensity = (min(inputs)+max(inputs))>>1
                
                # saturation
                saturation = max(inputs)-min(inputs)
                invSaturation = 1023-saturation

                WB = (870*intensity>>10,960*intensity>>10,225*intensity>>10,900*intensity>>10)
                smallest = min(inputs)
                colors = ((WB[0]+inputs[0]-smallest), (WB[1]+inputs[1]-smallest), (WB[2]+inputs[2]-smallest), WB[3])
                #print(str(colors))
                self._render.addPoint(colors[0],colors[1],colors[2],colors[3])
            except Exception as e:
                print(e)

a = ArtNetClient(Output)
