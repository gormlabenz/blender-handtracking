import c4d
from c4d import plugins, gui
import socket
import json

scale_factor = 1000
scale_sphere = 0.53


def receive_landmarks_from_server(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    message = "Request landmarks"
    client_socket.send(message.encode('utf-8'))

    response = client_socket.recv(4096)
    client_socket.close()

    return response.decode('utf-8')

def create_sphere(name, location):
    sphere = c4d.BaseObject(c4d.Osphere)
    sphere.SetName(name)
    sphere.SetRelPos(c4d.Vector(*location))
    sphere.SetRelScale(c4d.Vector(scale_sphere, scale_sphere, scale_sphere))
    return sphere

def update_landmarks():
    host = "localhost"
    port = 12345
    
    try:
        response_data_str = receive_landmarks_from_server(host, port)
    except ConnectionRefusedError:
        print(f"Connection to {host}:{port} refused")
        return
    except ConnectionResetError:
        print(f"Connection to {host}:{port} reset")
        return
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Process response data
    response_data = json.loads(response_data_str)
    landmark_data = json.loads(response_data['landmarks'])

    doc = c4d.documents.GetActiveDocument()

    # Iterate through landmarks and create/update spheres in Cinema 4D
    for index, landmark in enumerate(landmark_data):
        sphere_name = f"landmark_{index}"
        location = (
            landmark['x'] * scale_factor,
            landmark['z'] * scale_factor,
            landmark['y'] * - scale_factor)

        sphere = doc.SearchObject(sphere_name)
        if sphere is None:
            sphere = create_sphere(sphere_name, location)
            doc.InsertObject(sphere)
        else:
            sphere.SetRelPos(c4d.Vector(*location))

        c4d.EventAdd()

original_index_finger_tip = None


PLUGIN_ID = 1060816  # Choose a unique plugin ID (check c4d.PLUGINFLAG)

# Register the plugin
class TimerOperator(plugins.CommandData):

    def Execute(self, doc):
        update_landmarks()
        return True

if __name__ == "__main__":
    # Run the main loop
    def main_thread():
        import time
        while True:
            update_landmarks()
            time.sleep(1.0 / 15.0)

    import threading
    t = threading.Thread(target=main_thread)
    t.start()
