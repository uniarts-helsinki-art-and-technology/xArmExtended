from multiprocessing import Event
import time
from xarm.wrapper import XArmAPI
from threading import Thread, Lock, Event
from queue import Queue

__authors__ = ["Niklas Pollonen"]
__version__ = "0.0.001"

class XArmControl(Thread):
    def __init__(self, ip = "192.168.1.169", xyThreshold = 1):
        Thread.__init__(self)
        self.lock = Lock()
        self.running = Event()
        self.goToQueue = Queue()
        self.isConnected = False
        self.homingPosition = None

        # angles = True, radial = False
        self.is_radian = False

        self.xyzThreshold = xyThreshold
        self.radianThreshold =  0.3
        self.angularThreshold = 0.5

        # 0: position control mode
        # 1: servo motion mode
        #     Note: the use of the set_servo_angle_j interface must first be set to this mode
        #     Note: the use of the set_servo_cartesian interface must first be set to this mode
        # 2: joint teaching mode
        #     Note: use this mode to ensure that the arm has been identified and the control box and arm used for identification are one-to-one.
        # 3: cartesian teaching mode (invalid)
        # 4: joint velocity control mode
        # 5: cartesian velocity control mode
        # 6: joint online trajectory planning mode
        # 7: cartesian online trajectory planning mode
        self.mode = 0

        self.ip = ip
        self.connect(ip)
        # self.setNormalMode()
        self.initPosition()

    '''
        Common commands
    '''

    def connect(self, ip = "192.168.1.169"):
        try:
            self.arm = XArmAPI(ip, is_radian=True)
            self.isConnected = True
            print('Connected to ', ip)
            self.arm.clean_error()
            time.sleep(0.5)
            self.arm.clean_warn()
            self.arm.motion_enable(True)
            self.arm.set_mode(0)
            self.arm.set_state(0)
            #self.initPosition()
            return True
        except Exception as e:
            self.isConnected = False
            print(e)
            print("ERROR: Could not connect to Xarm")
            return False
    def initPosition(self):
        position = {'x':300, 'y':0, 'z':150, 'roll':180, 'pitch':0, 'yaw':0, 'speed':500, 'is_radian':False, 'wait':True}
        self.setPosition(**position)

    def disconnect(self):
        self.arm.disconnect()

    def home(self):

        self.initPosition()
        self.arm.move_gohome(wait=True)
        self.arm.reset(wait=True)
        self.position = self.homingPosition
        self.initPosition()

    def homeAndReset(self):
        if self.mode == 7:

            time.sleep(0.3)

            self.home()

            time.sleep(0.3)
            # self.arm.reset(wait=True)
            self.getArmPosition()
            self.getArmPositionRadial()
        else:
            time.sleep(0.3)
            self.home()

            time.sleep(1)
            # self.arm.reset(wait=True)
            self.getArmPosition()

    def waitForMovement(self):
        self.arm.reset(wait=True)

    def stop(self):
        self.running.set()

    def close(self):
        self.disconnect()
        self.stop()

    #   Normal movement mode: Accelerates and deaccelerates to the next position.
    #   Waits for movement to finish before executing the next move.

    def setNormalMode(self):
        print('setting mode 0')
        self.arm.set_mode(0)
        self.arm.set_state(state=0)
        self.arm.motion_enable(enable=True)
        time.sleep(1)

    # Tranjactory mode: Executes commands right after eachother and overrides with the next position.
    # Good for real-time movement because it executes the next move without stopping.
    def setTranjactoryMode(self):
        self.setMode(7)
        self.arm.set_state(state=0)
        self.arm.motion_enable(enable=True)
        time.sleep(1)

    def setMode(self, mode):
        if mode is not None and self.mode != mode and isinstance(mode, int):
            print('setting mode', mode)
            self.mode = mode
            self.arm.motion_enable(enable=True)
            self.arm.set_mode(mode)
            self.arm.set_state(state=0)


    '''
        Cartesian commands
    '''

    def updatePosition(self, pos):
        self.position.update(pos)

    def initPosition(self):
        code, pos = self.arm.get_position(is_radian=False)
        print('gotten pos', pos)
        # self.currentPosition = {'x': 87.0, 'y': 0.0, 'z': 154.199997, 'roll': 180.0, 'pitch': 0.0, 'yaw': 0.0, 'speed': 100.0, 'is_radian': False, 'wait': True}
        self.currentPosition = {'x':pos[0], 'y':pos[1], 'z':pos[2], 'roll':pos[3], 'pitch':pos[4], 'yaw':pos[5], 'speed': 100.0, 'is_radian': False, 'wait': True}
        self.position =  self.currentPosition
        self.homingPosition = self.currentPosition

    def getArmPosition(self):
        code, pos = self.arm.get_position(is_radian=False)
        self.currentPosition = {'x':pos[0], 'y':pos[1], 'z':pos[2], 'roll':pos[3], 'pitch':pos[4], 'yaw':pos[5]}
        return self.currentPosition

    def setArmPosition(self, x, y, z, roll, pitch, yaw, speed, is_radian=False, wait=True):
        print(x,y,z,roll,pitch,yaw,speed, is_radian, wait)
        self.arm.set_position(x=x, y=y, z=z, roll=roll, pitch=pitch, yaw=yaw, speed=speed, is_radian=is_radian, wait=wait)

    #    Position is added in format {'x':100, 'y':0, 'z':150, 'roll':0, 'pitch':0, 'yaw':0 'speed':100}
    #    or individual values {'z':150}


    def goToPosition(self, pos):
        self.position.update(pos)
        self.setArmPosition(**self.position)

    def getCurrentGotoPosition(self):
        return self.position

    '''
    Radian commands
    '''
    def getArmPositionRadial(self):
        code, pos = self.arm.get_position(is_radian=True)
        self.currentPositionRadial = {'x':pos[0], 'y':pos[1], 'z':pos[2], 'roll':pos[3], 'pitch':pos[4], 'yaw':pos[5]}
        return self.currentPositionRadial


    def setRadian(self, is_radian):
        if is_radian is not None:
            self.is_radian = is_radian

    def addToQueueTrajactory(self, pos, is_radian = False):
        self.goToQueue.put((pos, 7, is_radian))

    def addToQueue(self, pos, is_radian = False):
        self.goToQueue.put((pos, 0, is_radian))

    def moveQueuedMode(self):
        if not self.goToQueue.empty():

            if self.mode == 0:
                pos, mode, is_radian = self.goToQueue.get_nowait()
                self.position.update(pos)

                self.setMode(mode)
                self.setRadian(is_radian)
                self.goToPosition(self.position)
            elif self.mode == 7:
                if not self.is_radian:
                    if not ( abs(self.currentPosition['x'] - self.position['x']) > self.xyzThreshold
                        or abs(self.currentPosition['y'] -  self.position['y']) > self.xyzThreshold
                        or abs(self.currentPosition['z'] -  self.position['z']) > self.xyzThreshold
                        or abs(abs(self.currentPosition['roll']) -  abs(self.position['roll'])) > self.angularThreshold
                        or abs(self.currentPosition['yaw'] -  self.position['yaw']) > self.angularThreshold
                        or abs(self.currentPosition['pitch'] -  self.position['pitch']) > self.angularThreshold):


                        print("whaaa", abs(self.currentPosition['x'] - self.position['x']), abs(self.currentPosition['y'] -  self.position['y']))
                        pos, mode, is_radian = self.goToQueue.get_nowait()

                        self.position.update(pos)
                        if 'roll' in pos:
                            self.position.update({'roll': pos['roll']-360})

                        print(self.position)
                        self.setMode(mode)
                        self.setRadian(is_radian)
                        self.goToPosition(self.position)
                else:
                    if not ( abs(self.currentPosition['x'] - self.position['x']) > self.xyzThreshold
                        or abs(self.currentPosition['y'] -  self.position['y']) > self.xyzThreshold
                        or abs(self.currentPosition['z'] -  self.position['z']) > self.xyzThreshold
                        or abs(abs(self.currentPosition['roll']) -  self.position['roll']) > self.radianThreshold
                        or abs(self.currentPosition['yaw'] -  self.position['yaw']) > self.radianThreshold
                        or abs(self.currentPosition['pitch'] -  self.position['pitch']) > self.radianThreshold):
                            pos, mode, is_radian = self.goToQueue.get_nowait()
                            # if 'roll' in pos:
                            #     pos['roll'] *= -1

                            self.position.update(pos)
                            self.setMode(mode)
                            self.setRadian(is_radian)
                            self.goToPosition(self.position)

    def moveToTranjactory(self, pos):
        pos, mode, is_radian = self.goToQueue.get_nowait()

        self.position.update(pos)
        if 'roll' in pos:
            self.position.update({'roll': pos['roll']-360})

        print(self.position)
        self.setMode(mode)
        self.setRadian(is_radian)
        self.goToPosition(self.position)

    def run(self):
        while not self.running.is_set() and self.isConnected:
            if self.is_radian:
                self.getArmPositionRadial()
            else:
                self.getArmPosition()
            if self.mode == 0:
                self.moveQueuedMode()
            #7: tranjactory
            elif self.mode == 7:
                self.moveQueuedMode()
            elif self.mode == 3:
                if self.is_radian():
                    print('radial', self.getArmPositionRadial())
                else:
                    print('angular', self.getArmPosition())
