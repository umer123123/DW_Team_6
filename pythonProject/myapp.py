import random
import cv2
import cvzone
import streamlit as st
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import time

# Streamlit page config
st.set_page_config(page_title="Hand Gesture Game", layout="wide")

# Hand detector
detector = HandDetector(maxHands=1)

# Game variables
timer = 0
stateResult = False
startGame = False
scores = [0, 0]  # [AI, Player]

# Streamlit UI Elements
st.title("Rock Paper Scissors - Hand Gesture Game")
st.sidebar.header("Game Controls")

# Start Button
if st.sidebar.button("Start Game"):
    startGame = True
    initialTime = time.time()
    stateResult = False

# Capture image using Streamlit webcam
img_file = st.camera_input("Take a picture to play")

if img_file is not None:
    # Convert image file to OpenCV format
    file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)
    
    img = cv2.flip(img, 1)  # Flip for better interaction
    imgBG = cv2.imread("Resources/BG.png")
    
    # Resize webcam feed
    imgScaled = cv2.resize(img, (400, 300))
    
    # Detect hand
    hands, img = detector.findHands(img, draw=True)
    
    if startGame:
        if not stateResult:
            timer = time.time() - initialTime
            if timer > 3:
                stateResult = True
                timer = 0
                if hands:
                    playerMove = None
                    hand = hands[0]
                    fingers = detector.fingersUp(hand)

                    # Assign gestures
                    if fingers == [0, 0, 0, 0, 0]:
                        playerMove = 1  # Rock
                    elif fingers == [1, 1, 1, 1, 1]:
                        playerMove = 2  # Paper
                    elif fingers == [0, 1, 1, 0, 0]:
                        playerMove = 3  # Scissors

                    # AI move
                    aiMove = random.randint(1, 3)
                    imgAI = cv2.imread(f'Resources/{aiMove}.png', cv2.IMREAD_UNCHANGED)
                    imgBG = cvzone.overlayPNG(imgBG, imgAI, (149, 310))

                    # Determine winner
                    if (playerMove == 1 and aiMove == 3) or \
                       (playerMove == 2 and aiMove == 1) or \
                       (playerMove == 3 and aiMove == 2):
                        scores[1] += 1  # Player wins
                    elif (playerMove == 3 and aiMove == 1) or \
                         (playerMove == 1 and aiMove == 2) or \
                         (playerMove == 2 and aiMove == 3):
                        scores[0] += 1  # AI wins

    # Draw scores
    cv2.putText(imgBG, str(scores[0]), (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
    cv2.putText(imgBG, str(scores[1]), (1112, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)

    # Convert images for Streamlit
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    imgBG_RGB = cv2.cvtColor(imgBG, cv2.COLOR_BGR2RGB)

    # Display images in Streamlit
    col1, col2 = st.columns(2)
    with col1:
        st.image(imgRGB, caption="Captured Image", use_column_width=True)
    with col2:
        st.image(imgBG_RGB, caption="Game Screen", use_column_width=True)

    # Refresh UI
    time.sleep(0.1)
