import socket

# # IP address and port of the Arduino server
# arduino_ip = "192.168.1.102"  # IP address of your Arduino Nano ESP32
# arduino_port = 5555
#


class ArduinoCommunicator:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def send_message(self, message):
        print("Arduino message sent")
        if 1==1: #set to 1=2 for testing without actually using the arduino
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client_socket.connect((self.ip, self.port))
                client_socket.sendall(message.encode())
                print("Message sent successfully")
            except Exception as e:
                print(f"Error: {e}")
            finally:
                client_socket.close()
