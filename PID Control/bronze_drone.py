from microbit import * # NEEDS TO BE INCLUDED IN ALL CODE WRITTEN FOR MICROBIT
import radio
import math
import speech



# INITIALISE COMMANDS
# REMEMBER PARTY
scl1 = 3.5
scl2 = 5
off1 = 512
off2 = 521
radio_group=1
roll = 0
pitch = 0
yaw = 0
throttle = 0
arm = 0
RollSc = 0
PitchSc = 0
YawSc = 0
Throttlesc = 0
Armsc = 0

Pitchtel = 0
Yawtel = 0
Rolltel = 0
datalet = 0
battery = 0

#flight_mode = 737
flight_mode = 0

battery = 0

radio.on() # TURNS ON USE OF ANTENNA ON MICROBIT
radio.config(channel=radio_group) # A FEW PARAMETERS CAN BE SET BY THE PROGRAMMER
display.scroll(str(radio_group), wait=True, loop=False)
uart.init(baudrate=115200, bits=8, parity=None, stop=1, tx=pin1, rx=pin8)

def display_battery_level(b):

    battery_percent = ((b-300)/(1023-300))

    if battery_percent >= 0.6 and battery_percent < 0.8:
        display.set_pixel(4,0,0)
        display.set_pixel(4,1,9)
        display.set_pixel(4,2,9)
        display.set_pixel(4,3,9)
        display.set_pixel(4,4,9)

    elif battery_percent >= 0.4 and battery_percent < 0.6:
        display.set_pixel(4,0,0)
        display.set_pixel(4,1,0)
        display.set_pixel(4,2,9)
        display.set_pixel(4,3,9)
        display.set_pixel(4,4,9)

    elif battery_percent >= 0.2 and battery_percent < 0.4:
        display.set_pixel(4,0,0)
        display.set_pixel(4,1,0)
        display.set_pixel(4,2,0)
        display.set_pixel(4,3,9)
        display.set_pixel(4,4,9)

    elif battery_percent < 0.2:
        display.show(Image.SKULL)

    else:
        display.set_pixel(4,0,9)
        display.set_pixel(4,1,9)
        display.set_pixel(4,2,9)
        display.set_pixel(4,3,9)
        display.set_pixel(4,4,9)

def normalise(n, from_range, to_range):
    from_delta = from_range[1] - from_range[0]
    to_delta = to_range[1] - to_range[0]
    return (to_delta * (n - from_range[0]) // from_delta) + to_range[0]

def sendUart(roll, pitch, yaw, throttle, arm):
    global scl1, scl2, off1, off2, flight_mode
    if roll > 90:
        roll = 90
    elif roll < -90:
        roll = -90
    
    if pitch > 90:
        pitch = 90
    elif pitch < -90:
        pitch = -90
    
    if yaw > 90:
        yaw = 90
    elif yaw < -90:
        yaw = -90

    if throttle > 100:
        throttle = 100
    elif throttle < 0:
        throttle = 0
    
    RollSc = int((roll * scl1) + off2)
    PitchSc = int((pitch * scl1) + off1)
    YawSc = int((yaw * scl1) + off1)
    ThrottleSc = int((throttle * off1) / 50)
    ArmSc = int((arm * scl2) * 180)

# PREPARE CONTROLLER MESSAGE
    buf = []
    buf.extend(range(0,16,1))
    buf = bytearray(buf)
    
    buf[0] = 0
    buf[1] = 0x01
    buf[2] = (0 << 2) | ((RollSc >> 8) & 3)
    buf[3] = RollSc & 255
    buf[4] = (1 << 2) | ((PitchSc >> 8) & 3)
    buf[5] = PitchSc & 255
    buf[6] = (2 << 2) | ((ThrottleSc >> 8) & 3)
    buf[7] = ThrottleSc & 255
    buf[8] = (3 << 2) | ((YawSc >> 8) & 3)
    buf[9] = YawSc & 255
    buf[10] = (4 << 2) | ((ArmSc >> 8) & 3)
    buf[11] = ArmSc & 255
    buf[12] = (5 << 2) |((flight_mode >> 8) & 3)
    buf[13] = flight_mode & 255
    buf[14] = (6 << 2)
    buf[15] = 0
    uart.write(buf)
        
Roll_Off = 0
Pitch_Off = 0

for i in range(10):
    Roll_Off += normalise(accelerometer.get_x(), [-1024, 1023], [-90, 90])
    Pitch_Off += normalise(accelerometer.get_y(), [-1024, 1023], [-90, 90])

Roll_Off = Roll_Off / 10
Pitch_Off = Pitch_Off / 10

while True:
    
# RECEIVE COMMAND
    incoming = radio.receive()
# PARSE COMMAND
    if incoming:
        data_list = incoming.split(',')
        roll = int(data_list[1])
        pitch = int(data_list[2])
        yaw = int(data_list[3])
        throttle = int(data_list[4])
        arm = int(data_list[-1])
    
    sendUart(roll,pitch,yaw,throttle,arm)
    
    display.clear()
    if arm == 1:
        display.set_pixel(0, 0, 9)
    display.set_pixel(0, max(0, (-throttle // 20) + 4), 9)
    
    if (-90 <= roll <= 90 and -90 <= pitch <= 90):
            display.set_pixel(int(((roll + 108) / 180) * 4), int(((pitch + 108) / 180) * 4), 9)
    battery = pin0.read_analog()
    display_battery_level(battery)
    
    if uart.any():
        data = uart.read()
        datalist = list(data)
        if isinstance(datalist, list) and len(datalist) >= 9:
            Pitchtel = int(datalist[3]) - int(datalist[4])
            Rolltel = int(datalist[5]) - int(datalist[6])
            Yawtel = int(datalist[7]) + (int(datalist[8]) * 255)
            datalet = int(len(datalist))

    telemetry = str(Pitchtel) + "," + str(Yawtel) + "," + str(Rolltel) + "," + str(battery)
    radio.send(telemetry) 