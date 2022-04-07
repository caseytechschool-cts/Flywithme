import PySimpleGUI as sg
import base64
import os.path as path
from djitellopy import Tello
import cv2
import random

BAR_MAX = 100
TOTAL_ALLOWED_FLIPS = 2
flips = ["left", "right", "forward", "back"]


def image_to_base64(name):
    with open(path.join("images", name), "rb") as data:
        image_data = data.read()
        return base64.b64encode(image_data)


def main():
    # Make the drone connection
    tello = Tello()
    tello.connect()
    num_of_flips = 0
    recording = False
    takeoff = False

    status_bar = [sg.Text(text="Connected", size=(50, 1), justification="left", key="-conStatus-"),
           sg.Push(), sg.ProgressBar(BAR_MAX, orientation='h', key="-batStatus-", style='alt', size=(10, 5), border_width=3)]

    video_feed = [sg.Push(), sg.Image(source=image_to_base64("drone.png"), key="-image-"),
               sg.Push(), sg.Button(image_data=image_to_base64("camera_on.png"), key="-camera-", tooltip="Camera on")]

    movement_lrfb = [[sg.Push(), sg.Button(image_data=image_to_base64("up.png"), key="-forward-", tooltip="Move forward"), sg.Push()],
                     [sg.Button(image_data=image_to_base64("left.png"), key="-left-", tooltip="Move left"), sg.Push(),
                     sg.Button(image_data=image_to_base64("right.png"), key="-right-", tooltip="Move right")],
                     [sg.Push(), sg.Button(image_data=image_to_base64("down.png"), key="-backward-", tooltip="Move backward"), sg.Push()]]

    movement_flip = [[sg.Button(image_data=image_to_base64("flip.png"), key="-flip-", tooltip="Random flip"),
                     sg.Button(image_data=image_to_base64("front_flip.png"), key="-front_flip-", tooltip="Front flip"),
                     sg.Button(image_data=image_to_base64("back_flip.png"), key="-back_flip-", tooltip="Back flip")]]

    turn = [[sg.Button(image_data=image_to_base64("turn_sharp_left.png"), key="-sharp_left-", tooltip="Sharp left"),
            sg.Button(image_data=image_to_base64("turn_sharp_right.png"), key="-sharp_right-", tooltip="Sharp right"),
            sg.Button(image_data=image_to_base64("turn_slight_left.png"), key="-slight_left-", tooltip="Slight left"),
            sg.Button(image_data=image_to_base64("turn_slight_right.png"), key="-slight_right-", tooltip="Slight right")]]

    on_off = [[sg.Button(image_data=image_to_base64("takeoff.png"), key="-takeoff-", tooltip="Takeoff")]]

    layout = [status_bar, video_feed, [sg.Column(movement_lrfb), sg.VerticalSeparator(), sg.Column(movement_flip),
                                       sg.VerticalSeparator(), sg.Column(turn),
                                       sg.VerticalSeparator(), sg.Column(on_off)]
              ]

    window = sg.Window(title="  ::Tello Controller by CTS::  ",
                       layout=layout,
                       size=(1200, 800),
                       icon=image_to_base64("drone_ico.png"),
                       progress_bar_color=("green", "white"))

    while True:
        event, values = window.read(timeout=20)
        if event == "Exit" or event == sg.WIN_CLOSED:
            tello.land()
            tello.end()
            return

        # update the battery progress bar
        battery = tello.get_battery()
        # print(battery)
        window['-batStatus-'].update(battery)
        if battery <= 20:
            window['-batStatus-'].update(bar_color=("red", "white"))
            window['-conStatus-'].update(value="Swap the battery")
        else:
            window['-batStatus-'].update(bar_color=("green", "white"))

        if event == "-camera-":
            if not recording:
                window["-camera-"].update(image_data=image_to_base64("camera_off.png"))
                tello.streamon()
                frame_read = tello.get_frame_read()
                recording = True
            else:
                recording = False
                window["-camera-"].update(image_data=image_to_base64("camera_on.png"))
                tello.streamoff()

        if recording:
            window['-image-'].update(data=cv2.imencode('.png', frame_read.frame)[1].tobytes(), subsample=2)
        else:
            window["-image-"].update(data=image_to_base64("drone.png"))

        if not takeoff and event == "-takeoff-":
            takeoff = True
            window["-takeoff-"].update(image_data=image_to_base64("land.png"))
            tello.takeoff()

        elif takeoff and event == "-takeoff-":
            takeoff = False
            window["-takeoff-"].update(image_data=image_to_base64("takeoff.png"))
            tello.land()

        if event == "-forward-" and takeoff:
            tello.move_forward(20)

        if event == "-backward-" and takeoff:
            tello.move_back(20)

        if event == "-left-" and takeoff:
            tello.move_left(20)

        if event == "-right-" and takeoff:
            tello.move_right(20)

        if event == "-flip-" and takeoff and num_of_flips < TOTAL_ALLOWED_FLIPS:
            num_of_flips += 1
            random_flip = random.choices(flips)
            tello.flip(random_flip[0])

        if event == "-front_flip-" and takeoff and num_of_flips < TOTAL_ALLOWED_FLIPS:
            num_of_flips += 1
            tello.front_flip()

        if event == "-back_flip-" and takeoff and num_of_flips < TOTAL_ALLOWED_FLIPS:
            num_of_flips += 1
            tello.back_flip()

        if event == "-sharp_left-" and takeoff:
            tello.rotate_counter_clockwise(90)

        if event == "-sharp_right-" and takeoff:
            tello.rotate_clockwise(90)

        if event == "-slight_right-" and takeoff:
            tello.rotate_clockwise(30)

        if event == "-slight_left-" and takeoff:
            tello.rotate_counter_clockwise(30)


if __name__ == '__main__':
    main()
