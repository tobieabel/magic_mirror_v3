import soundfile as sf
import sounddevice as sd


def ask_for_input(mainwindow):
    print("insert code to ask for user input")

    mainwindow.fullscreen_window.show_request_info_screen()

    # Read the audio file - asks user for input
    data, sample_rate = sf.read("/Users/tobieabel/PycharmProjects/Magic_Mirror_v3/Model/Resources/Request Info.wav", dtype='int16')

    # Play the audio using sounddevice
    sd.play(data, samplerate=sample_rate, device=0)
    sd.wait()  # Wait until the audio is played

    #show face animation and text on mirror







