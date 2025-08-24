# gesture_controlled_powerpoint_extended.py

import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Webcam setup
cap = cv2.VideoCapture(0)

# Landmark IDs for the tips of the fingers
tip_ids = [4, 8, 12, 16, 20]

# Cooldown period to prevent multiple actions for a single gesture
cooldown_period = 1.5  # seconds
last_action_time = 0

print("Starting Gesture Controlled PowerPoint...")
print("Commands: Fist (End), 1 (Next), 2 (Prev), 3 (Start), 4 (Blank), 5 (First Slide)")

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Flip the image horizontally for a selfie-view display
    # and convert the BGR image to RGB.
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    
    # To improve performance, optionally mark the image as not writeable
    image.flags.writeable = False
    results = hands.process(image)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    lm_list = []
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Get landmark coordinates
            for id, lm in enumerate(hand_landmarks.landmark):
                h, w, c = image.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])

    # Gesture recognition logic
    if len(lm_list) != 0:
        fingers = []

        # Thumb (special case: checks horizontal position relative to wrist)
        # This logic is for a right hand in a mirror view.
        if lm_list[tip_ids[0]][1] > lm_list[tip_ids[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Other four fingers (checks vertical position)
        for id in range(1, 5):
            if lm_list[tip_ids[id]][2] < lm_list[tip_ids[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        
        total_fingers = fingers.count(1)
        
        # Check for cooldown
        current_time = time.time()
        if current_time - last_action_time > cooldown_period:
            
            # --- ACTION BLOCK ---
            # Perform actions based on the number of fingers
            
            # 0 Fingers (Closed Fist) -> End Slideshow
            if total_fingers == 0:
                print("Action: End Slideshow (Fist)")
                pyautogui.press('escape')
                last_action_time = current_time

            # 1 Finger -> Next Slide
            elif total_fingers == 1:
                print("Action: Next Slide (1 Finger)")
                pyautogui.press('right')
                last_action_time = current_time

            # 2 Fingers -> Previous Slide
            elif total_fingers == 2:
                print("Action: Previous Slide (2 Fingers)")
                pyautogui.press('left')
                last_action_time = current_time
            
            # 3 Fingers -> Start/Resume Slideshow
            elif total_fingers == 3:
                print("Action: Start Slideshow (3 Fingers)")
                pyautogui.press('f5')
                last_action_time = current_time

            # 4 Fingers -> Blank/Unblank Screen
            elif total_fingers == 4:
                print("Action: Blank Screen (4 Fingers)")
                pyautogui.press('b')
                last_action_time = current_time
            
            # 5 Fingers (Open Hand) -> Go to First Slide
            elif total_fingers == 5:
                print("Action: Go to First Slide (5 Fingers)")
                pyautogui.press('home')
                last_action_time = current_time


    # Display the resulting frame
    cv2.imshow('Gesture Controlled PowerPoint', image)

    # Exit condition
    if cv2.waitKey(5) & 0xFF == 27:  # Press 'Esc' to exit
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
hands.close()

print("Script finished.")

