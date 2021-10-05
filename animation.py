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


'''uFind: 

simple douple walker to find specific integer value, returns position if finds exact match.
if return is negative a new entry must be made in douple list
'''
def uFind(inputTuple, inVal):
    # if inputTuple is empty
    if len(inputTuple) == 0:
        return -1
    # if inVal is less than 1st item in the Douple
    if inputTuple[0] > inVal:
        return -1
    # find exact value
    for pointNr in range(len(inputTuple)):
            if inputTuple[pointNr] == inVal:
                return pointNr
    # find aporximate value 
    for pointNr in range(len(inputTuple)):
            if inputTuple[pointNr] > inVal:
                return -pointNr
    # input is larger
    return len(inputTuple)+1


'''Animation: object to manage animation playback with linear interpolation


1/200sec = 5uSec
timesystem?
'''
class animation:
    #values and timepoints should always be the same length
    _timepoints = ()
    _values = ()
    _baseTime = 0 #integer
    _baseKeyOffset = 0

    '''_tupleLenghtCheck:
    
    internal function to make sure the tuples are same lenght after reorganizing the arrays
    '''
    def _tupleLenghtCheck(self):
        if len(self._timepoints) == len(self._values) and len(self._timepoints) == len(self._interpolationStep):
            return 0
        else:
            return -1

    '''add new value @ time

    add new timepoint and value set timesorted order
    if the timepoint is allready defined the value is ovewritten
    '''
    def addPoint(self, timeIn:int, valueIn:int):
        newPos = uFind(self._timepoints, timeIn)

        # if value exists or the tuple will be longer
        if newPos > -1:
            if newPos > len(self._timepoints):
                self._timepoints += (timeIn,)
                self._values += (valueIn,)
                return

            newList = list(self._values)
            newList[newPos] = valueIn
            self._values = tuple(newList)
            return

        # if a new item needs to be added to the list the new position is negative
        else:
            if newPos == -1:
                self._timepoints = (timeIn,)+self._timepoints
                self._values = (valueIn,)+self._values
                return

            # split the arrays
            # kas listina saaks lihtsamalt?
            newPos = newPos * -1
            self._timepoints = self._timepoints[0:newPos]+(timeIn,)+self._timepoints[newPos+1:]
            self._values = self._values[0:newPos]+(valueIn,)+self._values[newPos+1:]
            return
    
    '''render:
    
    takes input in ms from the last render, returns value at time.
    if time is before 1st or after last keyframe the value is held
    '''
    def render(self, timeDelta):
        currentTime = self._baseTime + timeDelta
        print(currentTime)
        currentKey = self._timepoints[self._baseKeyOffset]
        nextKey = self._timepoints[self._baseKeyOffset+1]
        
        # if time is fruther than next key
        if currentTime >= nextKey:
            self._baseKeyOffset += 1
            nextKey = self._timepoints[self._baseKeyOffset+1]

        # interpolation length
        keyLength = nextKey-currentKey
        currPos = currentTime-currentKey

        print(currPos)
        print(uLerp(self._values[self._baseKeyOffset],self._values[self._baseKeyOffset+1],int(currPos/keyLength*1024)))

        self._baseTime = currentTime
        


a = animation()
a.addPoint(1000,255)
a.addPoint(2000,0)
a.addPoint(3000,512)
a.addPoint(4000,1023)

