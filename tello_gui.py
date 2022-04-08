import PySimpleGUI as sg
import base64
import os.path as path
from djitellopy import Tello
import cv2
import random
import threading

"""Things need to be included in
exception handling for tello commands.
Multithreading for the tello commands"""

BAR_MAX = 100
TOTAL_ALLOWED_FLIPS = 2
SHARP_ROTATE = 90
SLIGHT_ROTATE = 30
STEP_SIZE = 20
LOW_BATTERY_LEVEL = 20
flips = ["l", "r", "f", "b"]

"""A simple function for converting the source image into a base64 data for universal use.
:param name: (str) the name of the image file
:return: the base64 of the image file
"""


def image_to_base64(name):
    with open(path.join("images", name), "rb") as data:
        image_data = data.read()
        return base64.b64encode(image_data)


"""A simple function for receiving the video feed from the drone. Creates it's own thread for the non-blocking GUI.
:param name: frame_read: the frame_read object from the tello drone
 window: the window object from the PySimpleGUI
 :return: it puts the video data as the event outcome"""


def video_feed(frame_read, window):
    window.write_event_value("-video-data-", cv2.imencode('.png', frame_read.frame)[1].tobytes())


def main():
    sg.theme("SystemDefault")
    # Make the drone connection
    tello = Tello()
    tello.connect()
    num_of_flips = 0
    recording = False
    takeoff = False

    status_bar = [sg.Text(text="Connected", size=(50, 1), justification="left", key="-conStatus-"),
           sg.Push(), sg.ProgressBar(BAR_MAX, orientation='h', key="-batStatus-", style='alt', size=(10, 5), border_width=3)]

    video = [[sg.Push(), sg.Image(source=image_to_base64("drone.png"), key="-image-", subsample=2),
             sg.Push(), sg.Button(image_data=image_to_base64("camera_on.png"), key="-camera-", tooltip="Camera on", pad=65)],
             [sg.Text("---"*150)]]

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

    on_off = [[sg.Button(image_data=image_to_base64("takeoff.png"), key="-takeoff-", tooltip="Takeoff")],
              [sg.Button(image_data=image_to_base64("danger.png"), key="-danger-", tooltip="Emergency stop")]]

    layout = [status_bar, video, [sg.Column(movement_lrfb), sg.VerticalSeparator(), sg.Column(movement_flip),
                                  sg.VerticalSeparator(), sg.Column(turn),
                                  sg.VerticalSeparator(), sg.Column(on_off)]
              ]

    window = sg.Window(title="  ::Tello Controller by CTS::  ",
                       layout=layout,
                       size=(1200, 680),
                       icon=image_to_base64("drone_ico.png"),
                       progress_bar_color=("green", "white"))

    while True:
        event, values = window.read(timeout=20)
        if event == "Exit" or event == sg.WIN_CLOSED:
            if takeoff:
                tello.land()
                if recording:
                    tello.streamoff()
                tello.end()
            return

        # update the battery progress bar
        battery = tello.get_battery()
        window['-batStatus-'].update(battery)
        if battery <= LOW_BATTERY_LEVEL:
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
                # tello.streamoff()

        if recording:
            threading.Thread(target=video_feed, args=(frame_read, window), daemon=True).start()
            # window['-image-'].update(data=cv2.imencode('.png', frame_read.frame)[1].tobytes(), subsample=2)
        else:
            window["-image-"].update(data=image_to_base64("drone.png"), subsample=2)

        if event == "-video-data-" and recording:
            window['-image-'].update(data=values["-video-data-"], subsample=2)

        if not takeoff and event == "-takeoff-":
            takeoff = True
            window["-takeoff-"].update(image_data=image_to_base64("land.png"))
            tello.takeoff()

        elif takeoff and event == "-takeoff-":
            takeoff = False
            window["-takeoff-"].update(image_data=image_to_base64("takeoff.png"))
            tello.land()

        if event == "-danger-" and takeoff:
            takeoff = False
            window["-takeoff-"].update(image_data=image_to_base64("takeoff.png"))
            tello.emergency()

        if event == "-forward-" and takeoff:
            tello.move_forward(STEP_SIZE)

        if event == "-backward-" and takeoff:
            tello.move_back(STEP_SIZE)

        if event == "-left-" and takeoff:
            tello.move_left(STEP_SIZE)

        if event == "-right-" and takeoff:
            tello.move_right(STEP_SIZE)

        if event == "-flip-" and takeoff and num_of_flips < TOTAL_ALLOWED_FLIPS:
            num_of_flips += 1
            random_flip = random.choices(flips)
            tello.flip(random_flip[0])

        if event == "-front_flip-" and takeoff and num_of_flips < TOTAL_ALLOWED_FLIPS:
            num_of_flips += 1
            tello.flip_forward()

        if event == "-back_flip-" and takeoff and num_of_flips < TOTAL_ALLOWED_FLIPS:
            num_of_flips += 1
            tello.flip_back()

        if event == "-sharp_left-" and takeoff:
            tello.rotate_counter_clockwise(SHARP_ROTATE)

        if event == "-sharp_right-" and takeoff:
            tello.rotate_clockwise(SHARP_ROTATE)

        if event == "-slight_right-" and takeoff:
            tello.rotate_clockwise(SLIGHT_ROTATE)

        if event == "-slight_left-" and takeoff:
            tello.rotate_counter_clockwise(SLIGHT_ROTATE)


if __name__ == '__main__':
    main()
