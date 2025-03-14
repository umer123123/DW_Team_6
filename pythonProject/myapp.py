import random
import cv2
import cvzone
import streamlit as st
import numpy as np
import os
import time
from cvzone.HandTrackingModule import HandDetector
 
# Set Streamlit Page Config
st.set_page_config(page_title="Rock Paper Scissors - AI Hand Gesture", layout="wide")
 
# Initialize Hand Detector (for hand tracking)
detector = HandDetector(maxHands=1)
 
# Load Background Image (Ensure the file exists)
bg_path = "Resources/BG.png"
if not os.path.exists(bg_path):
    st.error("Error: 'Resources/BG.png' not found! Please upload it.")
else:
    imgBG = cv2.imread(bg_path)
 
# AI Move Images (Ensure files exist)
ai_moves = {i: f"Resources/{i}.png" for i in range(1, 4)}
for move in ai_moves.values():
    if not os.path.exists(move):
        st.error(f"Error: '{move}' not found! Please upload it.")
 
# Initialize Streamlit Session Variables
if "startGame" not in st.session_state:
    st.session_state.startGame = False
    st.session_state.scores = [0, 0]  # [AI, Player]
    st.session_state.timer = 0
    st.session_state.stateResult = False
    st.session_state.aiMove = None
    st.session_state.playerMove = None
    st.session_state.initialTime = 0
 
# Streamlit UI Elements
st.title("✋ Rock Paper Scissors - AI Hand Gesture Game")
 
# Sidebar Controls
st.sidebar.header("Game Controls")
if st.sidebar.button("Start Game"):
    st.session_state.startGame = True
    st.session_state.stateResult = False
    st.session_state.initialTime = time.time()
 
# Capture Image (Streamlit Camera Input)
uploaded_file = st.camera_input("📸 Take a picture of your hand gesture to play")
 
if uploaded_file is not None:
    # Convert uploaded image file to OpenCV format
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
 
    # Flip image for a natural user experience
    img = cv2.flip(img, 1)
 
    # Detect Hand
    hands, img = detector.findHands(img, draw=True)
 
    if st.session_state.startGame:
        if not st.session_state.stateResult:
            st.session_state.timer = time.time() - st.session_state.initialTime
 
            if st.session_state.timer > 3:
                st.session_state.stateResult = True
                st.session_state.timer = 0
 
                # Player Move Detection
                if hands:
                    hand = hands[0]
                    fingers = detector.fingersUp(hand)
 
                    # Assign move based on hand gesture
                    if fingers == [0, 0, 0, 0, 0]:
                        st.session_state.playerMove = 1  # Rock
                    elif fingers == [1, 1, 1, 1, 1]:
                        st.session_state.playerMove = 2  # Paper
                    elif fingers == [0, 1, 1, 0, 0]:
                        st.session_state.playerMove = 3  # Scissors
                    else:
                        st.warning("⚠️ Invalid hand gesture detected! Please try again.")
 
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
        ai_img = cv2.imread(ai_moves[st.session_state.aiMove], cv2.IMREAD_UNCHANGED)
        imgBG_display = cvzone.overlayPNG(imgBG_display, ai_img, (149, 310))
 
    # Convert Images to RGB for Streamlit
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    imgBG_RGB = cv2.cvtColor(imgBG_display, cv2.COLOR_BGR2RGB)
 
    # Display Images in Streamlit
    col1, col2 = st.columns(2)
    with col1:
        st.image(imgRGB, caption="Your Hand Gesture", use_column_width=True)
    with col2:
        st.image(imgBG_RGB, caption="Game Result", use_column_width=True)