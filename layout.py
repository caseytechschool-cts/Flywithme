import PySimpleGUI as sg
from base64image import image_to_base64
from constant import *
from pathmaker import resource_path

def layout_builder():
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
    return layout