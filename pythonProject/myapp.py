import random
import cv2
import cvzone
import streamlit as st
import numpy as np
import os
import time
from cvzone.HandTrackingModule import HandDetector
 
# Streamlit Page Configuration
st.set_page_config(page_title="Hand Gesture Game", layout="wide")
 
# Load Background Image (Check if it exists)
bg_path = "Resources/BG.png"
if not os.path.exists(bg_path):
    st.error("Error: 'Resources/BG.png' not found! Please upload it.")
else:
    imgBG = cv2.imread(bg_path)
 
# Load AI Move Images (1: Rock, 2: Paper, 3: Scissors)
ai_images = {i: f"Resources/{i}.png" for i in range(1, 4)}
for i in ai_images.keys():
    if not os.path.exists(ai_images[i]):
        st.error(f"Error: '{ai_images[i]}' not found! Please upload it.")
 
# Hand Detector
detector = HandDetector(maxHands=1)
 
# Initialize Streamlit Session State Variables
if "startGame" not in st.session_state:
    st.session_state.startGame = False
    st.session_state.scores = [0, 0]  # [AI, Player]
    st.session_state.timer = 0
    st.session_state.stateResult = False
    st.session_state.aiMove = None
    st.session_state.playerMove = None
    st.session_state.initialTime = 0
 
# UI Elements
st.title("✋ Rock Paper Scissors - Hand Gesture Game")
st.sidebar.header("Game Controls")
 
# Start Game Button
if st.sidebar.button("Start Game"):
    st.session_state.startGame = True
    st.session_state.stateResult = False
    st.session_state.initialTime = time.time()
 
# Webcam Input (Take Picture)
img_file = st.camera_input("Take a picture to play")
if img_file is not None:
    # Convert image file to OpenCV format
    file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
 
    # Flip image for better user experience
    img = cv2.flip(img, 1)
 
    # Detect Hand
    hands, img = detector.findHands(img, draw=True)
 
    if st.session_state.startGame:
        if not st.session_state.stateResult:
            st.session_state.timer = time.time() - st.session_state.initialTime
 
            if st.session_state.timer > 3:
                st.session_state.stateResult = True
                st.session_state.timer = 0
 
                # Player Move
                if hands:
                    hand = hands[0]
                    fingers = detector.fingersUp(hand)
 
                    # Mapping Hand Gestures to Moves
                    if fingers == [0, 0, 0, 0, 0]:
                        st.session_state.playerMove = 1  # Rock
                    elif fingers == [1, 1, 1, 1, 1]:
                        st.session_state.playerMove = 2  # Paper
                    elif fingers == [0, 1, 1, 0, 0]:
                        st.session_state.playerMove = 3  # Scissors
                    else:
                        st.warning("Invalid hand gesture! Please try again.")
 
                # AI Random Move
                st.session_state.aiMove = random.randint(1, 3)
 
                # Determine Winner
                if (
                    (st.session_state.playerMove == 1 and st.session_state.aiMove == 3) or
                    (st.session_state.playerMove == 2 and st.session_state.aiMove == 1) or
                    (st.session_state.playerMove == 3 and st.session_state.aiMove == 2)
                ):
                    st.session_state.scores[1] += 1  # Player Wins
 
                elif (
                    (st.session_state.playerMove == 3 and st.session_state.aiMove == 1) or
                    (st.session_state.playerMove == 1 and st.session_state.aiMove == 2) or
                    (st.session_state.playerMove == 2 and st.session_state.aiMove == 3)
                ):
                    st.session_state.scores[0] += 1  # AI Wins
 
    # Display Scores
    st.sidebar.write(f"🧠 AI Score: {st.session_state.scores[0]}")
    st.sidebar.write(f"🧑 Player Score: {st.session_state.scores[1]}")
 
    # Load Background and AI Move Image
    imgBG_display = imgBG.copy()
    if st.session_state.aiMove:
        ai_img = cv2.imread(ai_images[st.session_state.aiMove], cv2.IMREAD_UNCHANGED)
        imgBG_display = cvzone.overlayPNG(imgBG_display, ai_img, (149, 310))
 
    # Convert Images to RGB for Streamlit
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    imgBG_RGB = cv2.cvtColor(imgBG_display, cv2.COLOR_BGR2RGB)
 
    # Display Images
    col1, col2 = st.columns(2)
    with col1:
        st.image(imgRGB, caption="Your Hand", use_column_width=True)
    with col2:
        st.image(imgBG_RGB, caption="Game Result", use_column_width=True)