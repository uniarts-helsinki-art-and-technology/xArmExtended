from XArmControl import XArmControl
import sys
from oscReceiver import OSCReciever
import time
receiver = OSCReciever

__authors__ = ["Niklas Pöllönen"]
__version__ = "0.0.001"

arm = XArmControl()
__author__ = "Niklas Pöllönen"
__version__ = "0.001"

def main():
    try:
        # XY xyThreshold sets the SPEED of the machine
        speed = 500
        osc = OSCReciever()
        osc.start()
        arm.homeAndReset()
        arm.setNormalMode()
        arm.setTranjactoryMode()
        # initial position for drawing canvas    
        x_init = 100
        y_init = 0
        z_init = 150
        speed_init = speed

        # use to define size and depth of drawing area
        xy_multiplier = 0.5
        z_multipler = 1

        arm.goToPosition({'x':x_init, 'y':y_init, 'z':z_init, 'roll':180, 'pitch':0, 'yaw':0, 'speed':speed_init, 'is_radian':False, 'wait':True})

        # MAIN LOOP
        while 1:
            # get osc values

            #set timout delay commands
            #time.sleep(0.001)
            values = osc.get()
            if values:

                print(values)
                if values[0] == "/xyz":
                    msg, y,x, z = values
                    # send to machine
                    arm.goToPosition({'x':x_init+int(x)*xy_multiplier, 'y':y_init+int(y)*xy_multiplier, 'z':z_init+int(z)*z_multipler})
                    # debug
                    print("x:"+str(x)," y:"+str(y)," z:"+str(z))
                elif values[0] == "/xy":
                    msg, y, x = values
                    # send to machine
                    arm.goToPosition({'x':x_init+int(x)*xy_multiplier, 'y':y_init+int(y)*xy_multiplier})
                    # debug
                    print("x:"+str(x)," y:"+str(y))
                elif values[0] == "/z":
                    msg, z = values
                    # send to machine
                    arm.goToPosition({'z':z_init+int(z)*z_multipler})
                    # debug
                    print("z:",str(z))
        
    except KeyboardInterrupt:
        print('Interrupted')
        osc.stop()
        # arm.disconnect()
        sys.exit(0)
    print('Shutdown')

if __name__ == "__main__":
    main()

