import cv2
import mediapipe as mp
import socket
import json

# Socket client function
def send_landmarks_to_server(host, port, data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    client_socket.sendall(data.encode('utf-8'))
    client_socket.close()

# Convert landmarks to a JSON object
def landmarks_to_json(hand_landmarks):
    landmark_list = []
    for landmark in hand_landmarks.landmark:
        landmark_list.append({
            'x': landmark.x,
            'y': landmark.y,
            'z': landmark.z
        })
    return json.dumps(landmark_list)

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
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

                # Send the landmark data to the server
                landmark_data_json = landmarks_to_json(hand_landmarks)
                send_landmarks_to_server(server_host, server_port, landmark_data_json)

        cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
        if cv2.waitKey(5) & 0xFF == 27:
            break
cap.release()
