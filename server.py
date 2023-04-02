import socket
import json

received_landmarks = None
received_closed_fist = False

def create_socket_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(1)

    print(f"Server is listening on port {port}")
    return server_socket

def main():
    global received_landmarks, received_closed_fist

    port = 12345
    server_socket = create_socket_server(port)

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        data = client_socket.recv(4096)
        if data:
            data_str = data.decode('utf-8')
            if data_str.startswith("Request landmarks"):
                # Send the latest landmarks and closed_fist state to the Blender add-on
                if received_landmarks:
                    message = {
                        "landmarks": received_landmarks,
                        "closed_fist": received_closed_fist
                    }
                    client_socket.sendall(json.dumps(message).encode('utf-8'))
            else:
                # Store the received landmarks and closed_fist state from the hand tracking script
                message = json.loads(data_str)
                received_landmarks = message["landmarks"]
                received_closed_fist = message["closed_fist"]
                print(f"Received landmarks: {received_landmarks}")
                print(f"Closed Fist: {received_closed_fist}")

        client_socket.close()

if __name__ == "__main__":
    main()
