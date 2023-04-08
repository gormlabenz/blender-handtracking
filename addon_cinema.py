import c4d
from c4d import plugins, gui
import socket
import json

scale_factor = 30
scale_sphere = 0.53

# bone_name, parent_bone_name, mp_index, mp_name, relative, 
BONE_MAPPING = [
    ("rThumb1","rHand", 0, "WRIST", True),
    ("rCarpal1","rHand",0,"WRIST",True),
    ("rCarpal2","rHand",0,"WRIST",True),
    ("rCarpal3","rHand",0,"WRIST",True),
    ("rCarpal4","rHand",0,"WRIST",True),
    ("rForearmTwist","rForearmBend",0,"WRIST",True),
    ("rForearmBend", None,0,"WRIST",True),
    ("rHand","rForearmTwist",0,"WRIST"  ,False),
    ("rThumb2","rThumb1",2,"THUMB_MCP" ,False),
    ("rThumb3","rThumb2",3,"THUMB_IP",False),
    ("rIndex1","rCarpal1",5,"INDEX_FINGER_MCP" ,False),
    ("rIndex2","rIndex1",6,"INDEX_FINGER_PIP",False),
    ("rMid1","rCarpal2",9,"MIDDLE_FINGER_MCP",False),
    ("rMid2","rMid1",10,"MIDDLE_FINGER_PIP",False),
    ("rMid3","rMid2",11,"MIDDLE_FINGER_DIP",False),
    ("rRing1","rCarpal3",13,"RING_FINGER_MCP",False),
    ("rRing2","rRing1",14,"RING_FINGER_PIP",False),
    ("rRing3","rRing2",15,"RING_FINGER_DIP",False),
    ("rPinky1","rCarpal4",17,"PINKY_MCP",False),
    ("rPinky2","rPinky1",18,"PINKY_PIP",False),
    ("rPinky3","rPinky2",19,"PINKY_DIP",False),
]

def receive_landmarks_from_server(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    message = "Request landmarks"
    client_socket.send(message.encode('utf-8'))

    response = client_socket.recv(4096)
    client_socket.close()

    return response.decode('utf-8')

# Add a dictionary to store the initial positions of the bones
initial_positions = {}

# Function to store the initial positions of the bones
def store_initial_positions():
    doc = c4d.documents.GetActiveDocument()
    
    for bone_name, parent_bone_name, mp_index, mp_name, relative in BONE_MAPPING:
        bone = doc.SearchObject(bone_name)
        if not bone:
            continue
        initial_positions[bone_name] = bone.GetMg().off


def calculate_position_with_parent(parent_bone_name, position):
    doc = c4d.documents.GetActiveDocument()
    
    parent_bone = doc.SearchObject(parent_bone_name)
    if not parent_bone:
        return position
    parent_position = parent_bone.GetMg().off
    return position - parent_position

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
    
    # Iterate through the BONE_MAPPING and update the bone positions
    for bone_name, parent_bone_name, mp_index, mp_name, relative in BONE_MAPPING:
        bone = doc.SearchObject(bone_name)
        if not bone:
            continue

        landmark = landmark_data[mp_index]
        position = c4d.Vector(
            landmark['x'] * scale_factor,
            landmark['y'] * - scale_factor,
            landmark['z'] * scale_factor,
        )
        
        # Calculate the position with respect to the parent bone
        if parent_bone_name:
            position = calculate_position_with_parent(parent_bone_name, position)

        # Calculate the relative position manually
        if relative:
            initial_position = initial_positions[bone_name]
            position = initial_position + position

        bone.SetAbsPos(position)

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
        
        execution_time = 10
        loops = 0
        
        store_initial_positions()
        
        while True:
            update_landmarks()
            time.sleep(1.0 / 15.0)
            
            if loops > execution_time * 15:
                break
            
            loops += 1

    import threading
    t = threading.Thread(target=main_thread)
    t.start()
    
