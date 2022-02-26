from microbit import *
import radio
import math
import time

# INITIALISE COMMANDS
Pitch = 0
Arm = 0
Roll = 0
Throttle = 0
Yaw = 0
tel_roll = 0
tel_pitch = 0
# PID Gains
kp = 0.01
ki = 0.005
kd = 0
# PID VARIABLES
prev_time = 0
current_time = 0
rollTarget = 0
rollActual = 0
rollError = 0
rollErrorOld = 0
rollErrorChange = 0
rollErrorSlope = 0
rollErrorArea = 0
pitchTarget = 0
pitchActual = 0
pitchError = 0
pitchErrorOld = 0
pitchErrorChange = 0
pitchErrorSlope = 0
pitchErrorArea = 0
rollErrorAreaOld = 0
pitchErrorAreaOld = 0
counter = 0
# COMMUNICATIONS
radio_group=1
radio.on() # TURNS ON USE OF ANTENNA ON MICROBIT
radio.config(channel=radio_group) # A FEW PARAMETERS CAN BE SET BY THE PROGRAMMER
display.scroll(str(radio_group), wait=True, loop=False)

def display_battery_level(b)->none:

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

while True:
# PANIC FEATURE
    gesture = accelerometer.current_gesture()
    if gesture == "shake":
        Arm = 0

# ARM THE DRONE USING BOTH BUTTONS
    if button_a.is_pressed() and button_b.was_pressed():
        Throttle = 0
        if Arm == 0:
            Arm = 1
            rollErrorArea = 0
            pitchErrorArea = 0
        else:
            Arm = 0

 # RECEIVE COMMAND STRING
    cmd = radio.receive()
    if cmd:
        data_list = cmd.split(',')
        tel_roll = int(data_list[2])
        tel_pitch = int(data_list[0])
        battery = float(data_list[-1])
            
# PID CONTROL
    roll = tel_roll
    pitch = tel_pitch
    
    prev_time = current_time
    current_time = time.ticks_ms() / 1000
    dt = current_time - prev_time
   
    rollErrorOld = rollError
    rollError = rollTarget - rollActual
    rollErrorChange = rollError - rollErrorOld
    rollErrorSlope = rollErrorChange / dt
    rollErrorArea = rollErrorArea + rollError * dt
   
    Roll = int((rollError * kp) + (kd * rollErrorSlope) + (ki * rollErrorArea))
   
    pitchErrorOld = pitchError
    pitchError = pitchTarget - pitchActual
    pitchErrorChange = pitchError - pitchErrorOld
    pitchErrorSlope = pitchErrorChange / dt
    pitchErrorArea = pitchErrorArea + pitchError * dt
   
    Pitch = int((pitchError * kp) + (kd * pitchErrorSlope) + (ki * pitchErrorArea))

# SEND COMMAND STRING
    command = ""
    command = str(Roll)+ "," + str(Pitch * -1) + "," + str(Yaw) + "," + str(Throttle) + "," + str(Arm)
    radio.send(command)

# LED PLOTTING
    display.clear()
    if Arm == 1:
        display.set_pixel(0, 0, 9)
    display.set_pixel(0, normalise(Throttle, (0,100), (4,0)), 9)

    if (-90 <= Roll <= 90 and -90 <= Pitch <= 90):
        display.set_pixel(int(((Roll + 108) / 180) * 4), int(((Pitch + 108) / 180) * 4), 9)

    display_battery_level(battery)
# THROTTLE ADJUSTMENT
    if Arm == 1:
        if counter < 40:
            if Throttle < 80:
                Throttle += 2
        elif counter < 55:
            if Throttle > 65:
                Throttle -= 2
        elif counter < 75:
            if Throttle < 80:
                Throttle += 2
        else:
            counter = 40
        counter += 1
    else:
        Throttle = 0 
        counter = 0
    sleep(10)
