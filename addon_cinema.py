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
    closed_fist = response_data['closed_fist']

    # Update the camera position if a closed fist is detected
    # update_camera_position(closed_fist, landmark_data)

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

def update_camera_position(closed_fist, landmark_data):
    global original_index_finger_tip

    # Get the index finger tip landmark
    index_finger_tip = landmark_data[8]

    # Calculate the new camera position relative to the original position
    if original_index_finger_tip:
        camera_position = (
            (index_finger_tip['x'] * scale_factor) - 0.5 - original_index_finger_tip[0],
            (index_finger_tip['z'] * scale_factor) - 0.5 - original_index_finger_tip[1],
            (index_finger_tip['y'] * - scale_factor) - 0.5 - original_index_finger_tip[2]
        )
    else:
        camera_position = (
            (index_finger_tip['x'] * scale_factor) - 0.5,
            (index_finger_tip['z'] * scale_factor) - 0.5,
            (index_finger_tip['y'] * - scale_factor) - 0.5
        )

    if not closed_fist:
        original_index_finger_tip = camera_position
        return

    # Move the camera to the new position
    doc = c4d.documents.GetActiveDocument()
    bd = doc.GetActiveBaseDraw()
    camera = bd.GetSceneCamera(doc)
    camera.SetAbsPos(c4d.Vector(*camera_position))
    
PLUGIN_ID = 1060816  # Choose a unique plugin ID (check c4d.PLUGINFLAG)

# Register the plugin
class TimerOperator(plugins.CommandData):

    def Execute(self, doc):
        update_landmarks()
        return True

if __name__ == "__main__":
    """ bmp = c4d.bitmaps.BaseBitmap()
    bmp.Init(100, 100)

    result = plugins.RegisterCommandPlugin(
        PLUGIN_ID,
        "Handtracking",
        0,
        bmp,
        "Handtracking for Cinema 4D",
        TimerOperator())

    if result:
        print("Handtracking plugin registered successfully!")
    else:
        print("Handtracking plugin registration failed.") """

    # Run the main loop
    def main_thread():
        import time
        while True:
            update_landmarks()
            time.sleep(1.0 / 15.0)

    import threading
    t = threading.Thread(target=main_thread)
    t.start()
