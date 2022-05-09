import os
import sys

import PySimpleGUI as sg
import base64
import os.path as path
from djitellopy import Tello
import cv2
import random
import threading
import time

'''
MIT License

Copyright (c) 2018 DAMIÀ FUENTES ESCOTÉ

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

'''
MIT License

Copyright (c) 2022 Casey Tech School

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

BAR_MAX = 100
TOTAL_ALLOWED_FLIPS = 2
SHARP_ROTATE = 90
SLIGHT_ROTATE = 30
STEP_SIZE = 20
VELOCITY = 20
LOW_BATTERY_LEVEL = 20
flips = ["l", "r", "f", "b"]


def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


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
    time.sleep(1 / 30)


def drone_movement(tello, left_right, forward_backward, up_down, yaw):
    tello.send_rc_control(left_right, forward_backward, up_down, yaw)
    time.sleep(1 / 50)


def main():
    sg.theme("SystemDefault")
    num_of_flips = 0
    recording = False
    takeoff = False
    run_tello = False

    try:
        tello = Tello()
        tello.connect()
    except Exception as e:
        print(e)
    else:
        run_tello = True

    status_bar = [sg.Text(text="Not connected", size=(50, 1), justification="left", key="-conStatus-"),
                  sg.Push(), sg.ProgressBar(BAR_MAX, orientation='h', key="-batStatus-", style='alt', size=(10, 5),
                                            border_width=3)]

    video = [[sg.Push(), sg.Image(source=image_to_base64(resource_path("images/drone.png")), key="-image-", subsample=2),
              sg.Push(),
              sg.Button(image_data=image_to_base64(resource_path("images/camera_on.png")), key="-camera-", tooltip="Camera on", pad=65)],
             [sg.Text("---" * 150)]]

    movement_lrfb = [
        [sg.Push(), sg.Button(image_data=image_to_base64(resource_path("images/up.png")), key="-forward-", tooltip="Move forward"),
         sg.Push()],
        [sg.Button(image_data=image_to_base64(resource_path("images/left.png")), key="-left-", tooltip="Move left"), sg.Push(),
         sg.Button(image_data=image_to_base64(resource_path("images/right.png")), key="-right-", tooltip="Move right")],
        [sg.Push(), sg.Button(image_data=image_to_base64(resource_path("images/down.png")), key="-backward-", tooltip="Move backward"),
         sg.Push()]]

    movement_flip = [[sg.Button(image_data=image_to_base64(resource_path("images/flip.png")), key="-flip-", tooltip="Random flip"),
                      sg.Button(image_data=image_to_base64(resource_path("images/front_flip.png")), key="-front_flip-", tooltip="Front flip"),
                      sg.Button(image_data=image_to_base64(resource_path("images/back_flip.png")), key="-back_flip-", tooltip="Back flip")]]

    turn = [[sg.Button(image_data=image_to_base64(resource_path("images/turn_sharp_left.png")), key="-sharp_left-", tooltip="Sharp left"),
             sg.Button(image_data=image_to_base64(resource_path("images/turn_sharp_right.png")), key="-sharp_right-", tooltip="Sharp right"),
             sg.Button(image_data=image_to_base64(resource_path("images/turn_slight_left.png")), key="-slight_left-", tooltip="Slight left"),
             sg.Button(image_data=image_to_base64(resource_path("images/turn_slight_right.png")), key="-slight_right-",
                       tooltip="Slight right")]]

    on_off = [[sg.Button(image_data=image_to_base64(resource_path("images/takeoff.png")), key="-takeoff-", tooltip="Takeoff")],
              [sg.Button(image_data=image_to_base64(resource_path("images/danger.png")), key="-danger-", tooltip="Emergency stop")]]

    problem_bar = [[sg.Text("---" * 150)],
                   [sg.Push(), sg.Text(text="", text_color="red", key="-problem-bar-"), sg.Push()]]

    layout = [status_bar, video, [sg.Column(movement_lrfb), sg.VerticalSeparator(), sg.Column(movement_flip),
                                  sg.VerticalSeparator(), sg.Column(turn),
                                  sg.VerticalSeparator(), sg.Column(on_off)], problem_bar
              ]

    window = sg.Window(title="  ::Tello Controller by CTS::  ",
                       layout=layout,
                       size=(1200, 800),
                       icon=image_to_base64(resource_path("images/drone_ico.png")),
                       progress_bar_color=("green", "white"))

    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            if takeoff:
                try:
                    tello.send_command_without_return("land")
                    if recording:
                        try:
                            tello.streamoff()
                        except Exception as e:
                            print(e)
                    tello.end()
                except Exception as e:
                    print(e)
            else:
                if recording:
                    try:
                        tello.streamoff()
                    except Exception as e:
                        print(e)
                tello.end()
            return

        if run_tello:
            window["-conStatus-"].update(value="Connected")
            # update the battery progress bar
            try:
                battery = tello.get_battery()
            except Exception as e:
                print(e)
            else:
                window['-batStatus-'].update(battery)

                if battery <= LOW_BATTERY_LEVEL:
                    window['-batStatus-'].update(bar_color=("red", "white"))
                    window['-conStatus-'].update(value="Swap the battery")
                else:
                    window['-batStatus-'].update(bar_color=("green", "white"))

            if event == "-camera-":
                if not recording:
                    window["-camera-"].update(image_data=image_to_base64(resource_path("images/camera_off.png")))
                    try:
                        tello.streamon()
                    except Exception as e:
                        print(e)
                    else:
                        frame_read = tello.get_frame_read()
                        recording = True
                else:
                    recording = False
                    window["-camera-"].update(image_data=image_to_base64(resource_path("images/camera_on.png")))

            if recording:
                threading.Thread(target=video_feed, args=(frame_read, window), daemon=True).start()
            else:
                window["-image-"].update(data=image_to_base64(resource_path("images/drone.png")), subsample=2)

            if event == "-video-data-" and recording:
                window['-image-'].update(data=values["-video-data-"], subsample=2)

            if not takeoff and event == "-takeoff-":
                try:
                    threading.Thread(target=drone_movement, args=(tello, 0, 0, 0, 0), daemon=True).start()
                    tello.takeoff()
                except Exception as e:
                    print(e)
                else:
                    takeoff = True
                    window["-takeoff-"].update(image_data=image_to_base64(resource_path("images/land.png")))

            elif takeoff and event == "-takeoff-":
                try:
                    tello.send_command_without_return("land")
                except Exception as e:
                    print(e)
                else:
                    takeoff = False
                    window["-takeoff-"].update(image_data=image_to_base64(resource_path("images/takeoff.png")))

            if event == "-danger-" and takeoff:
                try:
                    tello.emergency()
                except Exception as e:
                    print(e)
                else:
                    takeoff = False
                    window["-takeoff-"].update(image_data=image_to_base64(resource_path("images/takeoff.png")))

            if event == "-forward-" and takeoff:
                try:
                    threading.Thread(target=drone_movement, args=(tello, 0, VELOCITY, 0, 0), daemon=True).start()
                except Exception as e:
                    print(e)

            if event == "-backward-" and takeoff:
                try:
                    threading.Thread(target=drone_movement, args=(tello, 0, -VELOCITY, 0, 0), daemon=True).start()
                except Exception as e:
                    print(e)

            if event == "-left-" and takeoff:
                try:
                    threading.Thread(target=drone_movement, args=(tello, -VELOCITY, 0, 0, 0), daemon=True).start()
                except Exception as e:
                    print(e)

            if event == "-right-" and takeoff:
                try:
                    threading.Thread(target=drone_movement, args=(tello, VELOCITY, 0, 0, 0), daemon=True).start()
                except Exception as e:
                    print(e)

            if event == "-flip-" and takeoff and num_of_flips < TOTAL_ALLOWED_FLIPS:
                try:
                    random_flip = random.choices(flips)
                    # tello.flip(random_flip[0])
                    tello.send_command_without_return("flip {}".format(random_flip[0]))
                except Exception as e:
                    print(e)
                else:
                    num_of_flips += 1

            if event == "-front_flip-" and takeoff and num_of_flips < TOTAL_ALLOWED_FLIPS:
                try:
                    # tello.flip_forward()
                    tello.send_command_without_return("flip f")
                except Exception as e:
                    print(e)
                else:
                    num_of_flips += 1

            if event == "-back_flip-" and takeoff and num_of_flips < TOTAL_ALLOWED_FLIPS:
                try:
                    # tello.flip_back()
                    tello.send_command_without_return("flip b")
                except Exception as e:
                    print(e)
                else:
                    num_of_flips += 1

            if event == "-sharp_left-" and takeoff:
                try:
                    threading.Thread(target=drone_movement, args=(tello, 0, 0, 0, -SHARP_ROTATE), daemon=True).start()
                except Exception as e:
                    print(e)

            if event == "-sharp_right-" and takeoff:
                try:
                    threading.Thread(target=drone_movement, args=(tello, 0, 0, 0, SHARP_ROTATE), daemon=True).start()
                except Exception as e:
                    print(e)

            if event == "-slight_right-" and takeoff:
                try:
                    threading.Thread(target=drone_movement, args=(tello, 0, 0, 0, SLIGHT_ROTATE), daemon=True).start()
                except Exception as e:
                    print(e)

            if event == "-slight_left-" and takeoff:
                try:
                    threading.Thread(target=drone_movement, args=(tello, 0, 0, 0, -SLIGHT_ROTATE), daemon=True).start()
                except Exception as e:
                    print(e)

            if num_of_flips >= TOTAL_ALLOWED_FLIPS or battery <= LOW_BATTERY_LEVEL:
                window["-problem-bar-"].update(value="You have reached the maximum allowed flips or battery is low.")
        else:
            window["-conStatus-"].update(value="Not connected")
            window["-problem-bar-"].update(value="Unable to establish connection")


if __name__ == '__main__':
    main()
