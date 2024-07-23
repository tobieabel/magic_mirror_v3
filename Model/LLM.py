import soundfile as sf
import sounddevice as sd


def ask_for_input(mainwindow):
    print("insert code to ask for user input")

    mainwindow.fullscreen_window.show_request_info_screen()

    # Read the audio file - asks user for input
    data, sample_rate = sf.read("/Users/tobieabel/PycharmProjects/Magic_Mirror_v3/Model/Resources/Request Info.mp3", dtype='int16')


    # Ensure the sample rate matches the audio file's sample rate
    print(f"Sample rate from file: {sample_rate}")

    # Play the audio using sounddevice
    sd.play(data, samplerate=sample_rate, device=0)  #device 0 is the monitor.  If the audio sounds garbled try restarting the Mac.
    sd.wait()  # Wait until the audio is played

    #show face animation and text on mirror







