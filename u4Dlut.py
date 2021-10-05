
def u4Dlut():
    _lut = [ (0.0, 255, 0, 0, 64),(0.5, 0, 255, 255,128),(1.0, 0, 0, 255, 255) ]

    def __init__(self, resolution=1024):
        self._resolution = resolution
        self._lookup = [(0,0,0,0)] * resolution

    def _find_color(x, vlist, lut):4
        """Finds linearly interpolated color from specified lut and x
        Returns RGBA tuple
        Parameters
        x: value to lookup5
        vlist: list of values in lut
        lut: List of tuples Value, R, G, B, A
        """
        last = len(lut) - 1 # last index for lut

        if x <= vlist[0] : #clamp low end
                return lut[0][1], lut[0][2], lut[0][3], lut[0][4]
        elif x >= vlist[last]: #clamp high end
                return lut[last][1], lut[last][2], lut[last][3], lut[last][4]
        else:
                # since vlist is sorted we can use bisect
                hi = bisect.bisect_left(vlist, x) #hi index
                lo = hi -  1 # lo index

                # interpolation weight from left
                w = ( x - vlist[lo] ) / (vlist[hi] -vlist[lo] )
                #print x, lo, hi, w

                # use w to interpolate r,g,b,a from lo and hi bins
                # interpolated_value = low_value + w * bin_size
                r = lut[lo][1]  + w * (lut[hi][1] - lut[lo][1])
                g = lut[lo][2]  + w * (lut[hi][2] - lut[lo][2])
                b = lut[lo][3]  + w * (lut[hi][3] - lut[lo][3])
                a = lut[lo][4]  + w * (lut[hi][4] - lut[lo][4])
                return int(r), int(g), int(b), int(a)


resolution = 1024
multiplier = float(resolution) / (lut[-1][0] - lut[0][0])
lookup = [(0, 0, 0, 0)] * resolution
for index in range(resolution):
    r, g, b, a = find_color(lut[0][0] + i / multiplier, vlist, lut)
    lookup[index] = (r, g, b, a)

def find_color2(x):
    return lookup[int((x - lut[0][0]) * multiplier)]