from thymio import *


@onevent
def light(r, g, b):
    nf_leds_top(r, g, b)


@onevent
def sound(frequency, duration):
    nf_sound_freq(frequency, duration)


@onevent
def move_forward(speed):
    global motor_left_target
    global motor_right_target
    motor_left_target = speed
    motor_right_target = speed


@onevent
def move_backward(speed):
    global motor_left_target
    global motor_right_target
    motor_left_target = -speed
    motor_right_target = -speed


@onevent
def stop():
    global motor_left_target
    global motor_right_target
    motor_left_target = 0
    motor_right_target = 0
