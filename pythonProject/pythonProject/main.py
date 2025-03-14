import random
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import time
import pygame  # Import pygame for sound effects

# Initialize pygame mixer
pygame.mixer.init()

# Load Sound Effects
sound_gameover = pygame.mixer.Sound("Resources/gameover.wav")
sound_ai_point = pygame.mixer.Sound("Resources/aipoint.wav")
sound_player_point = pygame.mixer.Sound("Resources/yourpoint.ogg")
sound_timer = pygame.mixer.Sound("Resources/timer.wav")  # Timer sound for round start

# Camera Setup
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Hand Detector
detector = HandDetector(maxHands=1)

# Game Variables
timer = 0
stateResult = False
startGame = False
scores = [0, 0]  # [AI, Player]
gameOver = False  # New flag to control game over state

while True:
    # Load Background
    imgBG = cv2.imread("Resources/BG.png")
    success, img = cap.read()

    imgScaled = cv2.resize(img, (0, 0), None, 0.875, 0.875)
    imgScaled = imgScaled[:, 80:480]

    # Find Hands
    hands, img = detector.findHands(imgScaled)  # with draw

    if startGame and not gameOver:

        if stateResult is False:
            timer = time.time() - initialTime
            cv2.putText(imgBG, str(int(timer)), (605, 435), cv2.FONT_HERSHEY_PLAIN, 6, (255, 0, 255), 4)

            if timer > 3:
                stateResult = True
                timer = 0

                if hands:
                    playerMove = None
                    hand = hands[0]
                    fingers = detector.fingersUp(hand)
                    if fingers == [0, 0, 0, 0, 0]:
                        playerMove = 1
                    if fingers == [1, 1, 1, 1, 1]:
                        playerMove = 2
                    if fingers == [0, 1, 1, 0, 0]:
                        playerMove = 3

                    randomNumber = random.randint(1, 3)
                    imgAI = cv2.imread(f'Resources/{randomNumber}.png', cv2.IMREAD_UNCHANGED)
                    imgBG = cvzone.overlayPNG(imgBG, imgAI, (149, 310))

                    # Player Wins a Round
                    if (playerMove == 1 and randomNumber == 3) or \
                            (playerMove == 2 and randomNumber == 1) or \
                            (playerMove == 3 and randomNumber == 2):
                        scores[1] += 1
                        pygame.mixer.Sound.play(sound_player_point)  # Play Player Score Sound

                    # AI Wins a Round
                    if (playerMove == 3 and randomNumber == 1) or \
                            (playerMove == 1 and randomNumber == 2) or \
                            (playerMove == 2 and randomNumber == 3):
                        scores[0] += 1
                        pygame.mixer.Sound.play(sound_ai_point)  # Play AI Score Sound

    imgBG[234:654, 795:1195] = imgScaled

    if stateResult:
        imgBG = cvzone.overlayPNG(imgBG, imgAI, (149, 310))

    # Display Scores
    cv2.putText(imgBG, str(scores[0]), (410, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)
    cv2.putText(imgBG, str(scores[1]), (1112, 215), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 6)

    # Check if the game is over (either AI or Player reaches 5 points)
    if scores[0] >= 5:
        winner_img = cv2.imread("Resources/lose.png", cv2.IMREAD_UNCHANGED)
        winner_img = cv2.resize(winner_img, (imgBG.shape[1], imgBG.shape[0]))  # Resize to fit BG
        pygame.mixer.Sound.play(sound_gameover)  # Play Game Over Sound
        gameOver = True

    elif scores[1] >= 5:
        winner_img = cv2.imread("Resources/win.png", cv2.IMREAD_UNCHANGED)
        winner_img = cv2.resize(winner_img, (imgBG.shape[1], imgBG.shape[0]))  # Resize to fit BG
        pygame.mixer.Sound.play(sound_gameover)  # Play Game Over Sound
        gameOver = True

    # Display Winner Screen if Game Over
    if gameOver:
        imgBG = winner_img  # Replace the background with the winner image

    # Show the images
    cv2.imshow("BG", imgBG)

    # Key Listeners
    key = cv2.waitKey(1)

    if key == ord('s') and not gameOver:  # Start game when 's' is pressed
        startGame = True
        initialTime = time.time()
        stateResult = False
        pygame.mixer.Sound.play(sound_timer)  # Play Timer Sound when game starts

    if key == ord('n') and gameOver:  # Reset game when 'n' is pressed
        scores = [0, 0]  # Reset scores
        gameOver = False
        startGame = False  # Wait for 's' to restart
