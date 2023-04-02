import socket
import time

received_landmarks = ""

def create_socket_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(1)

    print(f"Server is listening on port {port}")
    return server_socket

def main():
    global received_landmarks

    port = 12345
    server_socket = create_socket_server(port)

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        data = client_socket.recv(4096)
        if data:
            data_str = data.decode('utf-8')
            if data_str.startswith("Request landmarks"):
                # Send the latest landmarks to the Blender add-on
                if received_landmarks:
                    client_socket.sendall(received_landmarks.encode('utf-8'))
            else:
                # Store the received landmarks from the hand tracking script
                received_landmarks = data_str
                print(f"Received landmarks: {received_landmarks}")

        client_socket.close()
        time.sleep(0.05)  # Add a small delay (50 milliseconds)

if __name__ == "__main__":
    main()
