import PySimpleGUI as sg

def test_Click():
    print("I have been clicked")




def main():
    # Make the drone connection



    forward = [sg.Button(key="-forward-", tooltip="Move forward", button_text="Test")]
    # forward.click(test_Click)

    window = sg.Window(layout=[forward], title="Hello")

    while True:
        event, values = window.read(timeout=20)
        if event == "Exit" or event == sg.WIN_CLOSED:
            return
        if event == "-forward-":
            print("Clicked")
        # update the battery progress bar

        # forward.click(test_Click)




if __name__ == '__main__':
    main()
