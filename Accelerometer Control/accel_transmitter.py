from microbit import *
import radio
import math

# INITIALISE COMMANDS
Pitch = 0
Arm = 0
Roll = 0
Throttle = 0
Yaw = 0
tel_roll = 0
tel_pitch = 0
command = ""
# COMMUNICATIONS
radio_group=1
radio.on()
radio.config(channel=radio_group)
display.scroll(str(radio_group), wait=True, loop=False)

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
        else:
            Arm = 0
    if button_a.was_pressed():
        if Throttle <= 45:
            Throttle -= 5
        else:
            Throttle -= 1
            
    if button_b.was_pressed():
        if Throttle <= 45:
            Throttle += 5
        else:
            Throttle += 1

# RECEIVE COMMAND STRING
    cmd = radio.receive()
    if cmd:
        data_list = cmd.split(',')
        tel_roll = int(data_list[2])
        tel_pitch = int(data_list[0])
        battery = float(data_list[-1])
    
    Roll = normalise(accelerometer.get_x(), [-1024, 1023], [-90, 90])
    Pitch = normalise(accelerometer.get_y(), [-1024, 1023], [-90, 90])

# SEND COMMAND STRING
    command = str(Roll) + "," + str(Pitch * -1) + "," + str(Yaw) + "," + str(Throttle) + "," + str(Arm)
    radio.send(command)

# LED PLOTTING
    display.clear()
    if Arm == 1:
        display.set_pixel(0, 0, 9)
    display.set_pixel(0, normalise(Throttle, (0,100), (4,0)), 9)

    if (-90 <= Roll <= 90 and -90 <= Pitch <= 90):
        display.set_pixel(int(((Roll + 108) / 180) * 4), int(((Pitch + 108) / 180) * 4), 9)

    display_battery_level(battery)
    sleep(10)
