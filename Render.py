import machine
import time
import LM75

'''TODO list:

[X] - Implement render cycle (values are updated every 0.01, ie 10ms)
[X] - Implement red ch calibration
[X] - Test if output is running 100fps
[X] - Try 200fps
[X] - 0.08s point chaser (16 step)

[X] - bring over the PWM and Pin assignment
[X] - Render module to setup.py
[X] - Automatic Red calibarition read @ 1s, adjust at every 6 sec
[ ] - Artnet on 5600K (100% only calibrated)
[ ] - WB range (100% only claibrated)
[ ] - WB intensity calibration

[ ] - Colorwheel LUT
[ ] - Render timing profiling (autospeed?)

'''

class Render():
    __renderWindowMS = 5
    __PWM = 19000
    _rInput = 0
    _gInput = 0
    _bInput = 0
    _wInput = 0
    _rStep = 0
    _gStep = 0
    _bStep = 0
    _wStep = 0
    _currentStep = 0
    _currentTemp = 600

    _r = 0
    _g = 0
    _b = 0
    _w = 0

    def __init__(self, i2cInterface, rPin=21, gPin=19, bPin=18, wPin=4):
        # generate hardware PWM outputs per channels
        self._pwm = []
        self._pwm.append(machine.PWM(machine.Pin(rPin)))
        self._pwm.append(machine.PWM(machine.Pin(gPin)))
        self._pwm.append(machine.PWM(machine.Pin(bPin)))
        self._pwm.append(machine.PWM(machine.Pin(wPin)))
        self._pwm[0].freq(19000)

        # init temp calibartion
        self.genRedLut()

        self._tempSensor = LM75.LM75(i2cInterface,0x4f)
        self._tempValues = []
        self._tempTimer = machine.Timer(2)
        self._tempTimer.init(period=1000, mode=machine.Timer.PERIODIC, callback=self.updateTemp)

        # initiate render function periodically
        self._timer = machine.Timer(1)
        self._timer.init(period=self.__renderWindowMS, mode=machine.Timer.PERIODIC, callback=self.render)
    

        # set the deadline for the 1st render to finish
        self._deadline = time.ticks_add(time.ticks_ms(), self.__renderWindowMS)
        
    def updateTemp(self,caller):
        if len(self._tempValues) < 7:
            sensor = self._tempSensor.get_temp()
            # multiply values by 10 (to avoid float)
            self._tempValues.append((sensor[0]*10+sensor[1])) 
        else:
            self._currentTemp = self._tempValues[3]
            self._tempValues = []

    def addPoint(self,inR,inG,inB,inW):
        self._rInput = self._r
        self._gInput = self._g
        self._bInput = self._b
        self._wInput = self._w

        self._r = inR
        self._g = inG
        self._b = inB
        self._w = inW

        self._rStep = abs(self._r-self._rInput)>>4
        self._gStep = abs(self._g-self._gInput)>>4
        self._bStep = abs(self._b-self._bInput)>>4
        self._wStep = abs(self._w-self._wInput)>>4

        # if the step is smaller than 1 codevalue (bitshift returns instad of -0 -> -1)
        if self._rInput > self._r:
            self._rStep *=-1
    
        if self._gInput > self._g:
            self._gStep *=-1

        if self._bInput > self._b:
            self._bStep *=-1

        if self._wInput > self._w:
            self._wStep *=-1

        self._currentStep = 0

    def genRedLut(self):
        lut= []
        for i in range(1024):
            # 0.43 codevalues per 1C base -30@ 49.9% ie 513 codevalue 
            lut.append(round(i*0.43)+513)
        self._redLut = tuple(lut)

    def render(self, caller):
        
        # point chaser
        localR = self._rInput+(self._rStep*self._currentStep)
        localG = self._gInput+(self._gStep*self._currentStep)
        localB = self._bInput+(self._bStep*self._currentStep)
        localW = self._wInput+(self._wStep*self._currentStep)

        # if step is smaller than 1
        if self._rStep == 0: localR = self._r
        if self._gStep == 0: localG = self._g
        if self._bStep == 0: localB = self._b
        if self._wStep == 0: localW = self._w

        # advance or reset the the stepper // TODO lambda?
        if self._currentStep == 16:
            localR = self._r
            localG = self._g
            localB = self._b
            localW = self._w
            self.addPoint(localR,localG,localB,localW)
        else:
            self._currentStep += 1

        # output
            # add 30C to adjust for the -30C starting point
        compensatedRed = self._redLut[self._currentTemp+300]*localR>>10
        self._pwm[0].duty(compensatedRed) # calibrate the Red CH
        self._pwm[1].duty(localG)
        self._pwm[2].duty(localB)
        self._pwm[3].duty(localW)
        self._renderBudgetMS = time.ticks_diff(self._deadline, time.ticks_ms())
        self._deadline = time.ticks_add(time.ticks_ms(), self.__renderWindowMS)