import PySimpleGUI as sg
from djitellopy import Tello
import cv2
import random
import threading
import time
from layout import layout_builder
from pathmaker import resource_path
from base64image import image_to_base64
from constant import *

'''
MIT License

Copyright (c) 2022 Casey Tech School

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

    layout = layout_builder()

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
