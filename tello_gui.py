import PySimpleGUI as sg
import base64
import os.path as path
from djitellopy import Tello
import cv2

BAR_MAX = 100


def image_to_base64(name):
    with open(path.join("images", name), "rb") as data:
        image_data = data.read()
        return base64.b64encode(image_data)


def main():
    # Make the drone connection
    tello = Tello()
    tello.connect()
    tello.streamon()

    frame_read = tello.get_frame_read()
    recording = False

    col = [sg.Text(text="Connected", size=(50, 5), justification="left", key="-conStatus-"),
               sg.Push(), sg.ProgressBar(BAR_MAX, orientation='h', key="-batStatus-", style='alt', border_width=5, size_px=(100,10))]

    layout = [sg.Column(col, vertical_alignment='center'),
              [sg.Image(source=image_to_base64("drone.png"), size=(600, 400), key="-image-"),
               sg.Button(image_data=image_to_base64("camera_on.png"), key="-camera-")]]

    window = sg.Window(title="  ::Tello Controller by CTS::  ",
                       layout=layout,
                       size=(1200, 800),
                       icon=image_to_base64("drone_ico.png"),
                       element_justification="center")

    while True:
        event, values = window.read(timeout=20)
        if event == "Exit" or event == sg.WIN_CLOSED:
            return

        # update the battery progress bar
        battery = tello.get_battery()
        # print(battery)
        window['-batStatus-'].update(battery)
        if battery <= 20:
            window['-batStatus-'].update(bar_color="red")
            window['-conStatus-'].update(value="Swap the battery")
        else:
            window['-batStatus-'].update(bar_color="green")

        if event == "-camera-":
            window["-camera-"].update(disabled=True)
            recording = True

        if recording:
            # ret, frame = cap.read()
            imgbytes = cv2.imencode('.png', frame_read.frame)[1].tobytes()  # ditto
            # print(frame_read.frame)
            window['-image-'].update(data=imgbytes)


if __name__ == '__main__':
    main()
