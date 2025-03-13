import streamlit as st
import cv2
import numpy as np
import pickle
import face_recognition
import tempfile

# Load trained model
def load_trained_model():
    with open("face_embeddings.pkl", "rb") as f:
        data = pickle.load(f)
    return data["encodings"], data["names"]

def recognize_face(frame):
    encodings, names = load_trained_model()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, faces)

    for face_encoding, face_location in zip(face_encodings, faces):
        distances = face_recognition.face_distance(encodings, face_encoding)
        min_distance = min(distances)
        if min_distance < 0.6:
            match_index = distances.argmin()
            name = names[match_index]
        else:
            name = "Unknown"
        
        top, right, bottom, left = face_location
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    return frame

# Streamlit App
st.title("Face Identification System")
option = st.sidebar.selectbox("Choose Mode", ["Upload Video", "Webcam"])

if option == "Upload Video":
    uploaded_file = st.file_uploader("Upload a video", type=["mp4", "avi", "mov"])
    if uploaded_file:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_file.read())
        cap = cv2.VideoCapture(tfile.name)
        stframe = st.empty()
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = recognize_face(frame)
            stframe.image(frame, channels="BGR")
        cap.release()

elif option == "Webcam":
    cap = cv2.VideoCapture(0)
    stframe = st.empty()
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = recognize_face(frame)
        stframe.image(frame, channels="BGR")
    cap.release()
