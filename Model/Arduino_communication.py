import socket

# IP address and port of the Arduino server
arduino_ip = "192.168.1.102"  # IP address of your Arduino Nano ESP32
arduino_port = 5555

# Messages to send to the Arduino server
LOCK = "Lock"
UNLOCK = 'Unlock'

def Arduino(message):
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to the Arduino server
        client_socket.connect((arduino_ip, arduino_port))

        # Send the message
        client_socket.sendall(message.encode())
        print("Message sent successfully")

    except Exception as e:
        print("Error:", e)

    finally:
        # Close the socket connection
        client_socket.close()


class ArduinoCommunicator:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def send_message(self, message):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((self.ip, self.port))
            client_socket.sendall(message.encode())
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()
