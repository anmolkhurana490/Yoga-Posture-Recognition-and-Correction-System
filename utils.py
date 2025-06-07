<<<<<<< HEAD
import cv2
import numpy as np
import mediapipe as mp
import base64
import warnings

from keras import models
# import torch
# from ai_model.models import YogaModel 

# Suppress warnings from deep learning libraries
warnings.filterwarnings('ignore')

# Load the PyTorch model
# model = YogaModel()
# model.load_state_dict(torch.load("ai_model/yoga_posture_model.pth", map_location=torch.device('cpu')))
# model.eval()
model = models.load_model('ai_model/yoga_trainer_model.keras')

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

def generate_keypoints(frame):
    results = pose.process(frame)
    pose_pred = None

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        keypoints = np.array([[lm.x, lm.y, lm.z] for lm in landmarks])
        return keypoints, results.pose_landmarks
    
    return None, None

def draw_landmarks(frame, landmarks):
    # landmarks = [mp.python.solutions.pose.PoseLandmark(x=kp[0], y=kp[1], z=kp[2]) for kp in keypoints]
    # pose_landmarks = mp.framework.formats.landmark_pb2.NormalizedLandmarkList(landmark=landmarks)
    mpDraw.draw_landmarks(frame, landmarks, mp_pose.POSE_CONNECTIONS)

# decode image from base64 format
def decode_image(image_data):
    image_data = image_data.split(',')[1]
    image_data = base64.b64decode(image_data)
    np_arr = np.frombuffer(image_data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return frame

# encode image into base64 format
def encode_image(image_frame):
    _, buffer = cv2.imencode('.jpg', image_frame)
    return base64.b64encode(buffer).decode('utf-8')

def model_predict_pose(data_batch):
    # input_tensor = torch.tensor(keypoints.flatten(), dtype=torch.float32).unsqueeze(0)

    # with torch.no_grad():
    #     prediction = model(input_tensor)
    # keypoints = np.expand_dims(keypoints, axis=0)
    ypred = model.predict(np.array(data_batch), verbose=0)
    uniq_vals, counts = np.unique(ypred.argmax(axis=1), return_counts=True)
    return uniq_vals[counts.argmax()]

def read_file(filePath):
    with open(filePath, 'r') as file:
=======
import cv2
import numpy as np
import mediapipe as mp
import base64
import warnings

from keras import models
# import torch
# from ai_model.models import YogaModel 

# Suppress warnings from deep learning libraries
warnings.filterwarnings('ignore')

# Load the PyTorch model
# model = YogaModel()
# model.load_state_dict(torch.load("ai_model/yoga_posture_model.pth", map_location=torch.device('cpu')))
# model.eval()
model = models.load_model('ai_model/yoga_trainer_model.keras')

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

def generate_keypoints(frame):
    results = pose.process(frame)
    pose_pred = None

    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        keypoints = np.array([[lm.x, lm.y, lm.z] for lm in landmarks])
        return keypoints, results.pose_landmarks
    
    return None, None

def draw_landmarks(frame, landmarks):
    # landmarks = [mp.python.solutions.pose.PoseLandmark(x=kp[0], y=kp[1], z=kp[2]) for kp in keypoints]
    # pose_landmarks = mp.framework.formats.landmark_pb2.NormalizedLandmarkList(landmark=landmarks)
    mpDraw.draw_landmarks(frame, landmarks, mp_pose.POSE_CONNECTIONS)

# decode image from base64 format
def decode_image(image_data):
    image_data = image_data.split(',')[1]
    image_data = base64.b64decode(image_data)
    np_arr = np.frombuffer(image_data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return frame

# encode image into base64 format
def encode_image(image_frame):
    _, buffer = cv2.imencode('.jpg', image_frame)
    return base64.b64encode(buffer).decode('utf-8')

def model_predict_pose(data_batch):
    # input_tensor = torch.tensor(keypoints.flatten(), dtype=torch.float32).unsqueeze(0)

    # with torch.no_grad():
    #     prediction = model(input_tensor)
    # keypoints = np.expand_dims(keypoints, axis=0)
    ypred = model.predict(np.array(data_batch), verbose=0)
    uniq_vals, counts = np.unique(ypred.argmax(axis=1), return_counts=True)
    return uniq_vals[counts.argmax()]

def read_file(filePath):
    with open(filePath, 'r') as file:
>>>>>>> 05992ff7e32145a539c93fe1f22efdb9c8e4905e
        return file.read()