import cv2
import mediapipe as mp
import socket
import json

# Socket client function
def send_landmarks_to_server(host, port, data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    try:
        client_socket.sendall(data.encode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")
    client_socket.close()

previous_smoothed_landmarks = None
smoothing_factor = 0.5

# Convert landmarks to a JSON object
def landmarks_to_json(landmarks):
    global previous_smoothed_landmarks
    
    json_data = []
    landmark_list = []
    
    for index, landmark in enumerate(landmarks.landmark):
        landmark_dict = {
                "x": landmark.x - 0.5, 
                "y": landmark.y - 0.5, 
                "z": landmark.z - 0.5
                }
         
        if previous_smoothed_landmarks is not None:
            landmark_dict = {
                "x": (landmark.x -0.5) * (1 - smoothing_factor) + previous_smoothed_landmarks[index]["x"]  * smoothing_factor, 
                "y": (landmark.y-0.5) * (1 - smoothing_factor) + previous_smoothed_landmarks[index]["y"]  * smoothing_factor, 
                "z": (landmark.z-0.5) * (1 - smoothing_factor) + previous_smoothed_landmarks[index]["z"]  * smoothing_factor
                }
            
        landmark_list.append(landmark_dict)
        json_data.append(landmark_dict)
            
    previous_smoothed_landmarks = landmark_list
            
    return json.dumps(json_data)

def is_closed_fist(landmarks):
    thumb_tip = landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_finger_tip = landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

    distance = ((thumb_tip.x - index_finger_tip.x) ** 2 +
                (thumb_tip.y - index_finger_tip.y) ** 2 +
                (thumb_tip.z - index_finger_tip.z) ** 2) ** 0.5

    return distance < 0.1

# Hand tracking and drawing utilities
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# Socket server address and port
server_host = "localhost"
server_port = 12345

# For webcam input:
cap = cv2.VideoCapture(1)
with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # ... (rest of the drawing code)

                # Send landmarks and closed_fist state to the server
                landmark_data_str = landmarks_to_json(hand_landmarks)
                closed_fist = is_closed_fist(hand_landmarks)
                message = {"landmarks": landmark_data_str, "closed_fist": closed_fist}
                send_landmarks_to_server(server_host, server_port, json.dumps(message))


        cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
        if cv2.waitKey(5) & 0xFF == 27:
            break
cap.release()
