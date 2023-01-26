from XArmControl import XArmControl
import sys, math
from oscReceiver import OSCReciever
import time
receiver = OSCReciever
__authors__ = ["Niklas Pollonen"]
__version__ = "0.0.001"

# PLAY WITH THIS-----
# XY xyThreshold sets the SPEED and PRECITION

arm = XArmControl(xyThreshold=5)

def distBetween2Points( x1, y1, z1, x2, y2, z2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)


def main():
    # init receiver
    osc = OSCReciever()

    # init xarm
    try:
        osc.start()
        arm.start()
        arm.homeAndReset()
        arm.setNormalMode()
        arm.setTranjactoryMode()

        # initial position for drawing canvas
        x_init = 100
        y_init = 0
        z_init = 150
        speed_init = 500

        timeTolerance = 0.001
        distanceTolerance = 5

        lastPoint = [0,0,0]

        # use to define size and depth of drawing area
        xy_multiplier = 0.5
        z_multipler = 1
        time.sleep(0.5)
        arm.addToQueueTrajactory({'x':x_init, 'y':y_init, 'z':z_init,'speed':speed_init, 'is_radian':False, 'wait':True})
        lastTime = time.time()
        # MAIN LOOP
        while 1:
            #set timout delay commands
            time.sleep(0.001)
            values = osc.get()
            if values:
                if values[0] == "/xyz":
                        msg, y,x,z = values
                        if(abs(distBetween2Points(x, y, z, lastPoint[0], lastPoint[1], lastPoint[2])) >= distanceTolerance or time.time() - lastTime > timeTolerance):
                            arm.addToQueueTrajactory({'x':x_init+int(x)*xy_multiplier, 'y':y_init+int(y)*xy_multiplier, 'z':z_init+int(z)*z_multipler})
                            # debug
                            lastPoint[0] = x
                            lastPoint[1] = y
                            lastPoint[2] = z
                            lastTime = time.time()
                            #print("x:"+str(x)," y:"+str(y)," z:"+str(z))
                elif values[0] == "/xy":
                    msg, y, x = values
                    if(abs(math.dist(x, y, lastPoint[0], lastPoint[1])) >= distanceTolerance or time.time() - lastTime > timeTolerance):
                        arm.addToQueueTrajactory({'x':x_init+int(x)*xy_multiplier, 'y':y_init+int(y)*xy_multiplier})
                        # debug
                        lastPoint[0] = x
                        lastPoint[1] = y
                        lastTime = time.time()
                        #print("x:"+str(x)," y:"+str(y))

                elif values[0] == "/z":
                        msg, z = values
                        if(abs(z-lastPoint[2]) >= distanceTolerance or time.time() - lastTime > timeTolerance):
                            arm.addToQueueTrajactory({'z':z_init+int(z)*z_multipler})
                            # debug
                            lastPoint[2] = z
                            lastTime = time.time()
                            #print("z:",str(z))

    except KeyboardInterrupt:
        print('Interrupted')
        osc.stop()
        # arm.disconnect()
        sys.exit(0)
    print('Shutdown')

if __name__ == "__main__":
    main()
