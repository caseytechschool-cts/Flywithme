import PySimpleGUI as sg
import base64
import os.path as path
from djitellopy import Tello
import cv2


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

    cap = cv2.VideoCapture(0)
    recording = False

    layout = [[sg.Text("Connected", size=(50, 1), justification="left", key="-conStatus-"),
               sg.Text(f"Battery: {tello.get_battery()}%", size=(100, 1), justification="right", key="-batStatus-")],
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
