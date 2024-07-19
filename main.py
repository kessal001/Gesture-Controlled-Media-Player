import mediapipe as mp
import cv2
import math
import pyautogui
import time

# Initialize MediaPipe Hands and Drawing utilities
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Open webcam
capture = cv2.VideoCapture(0)

def calculate_distance(point1, point2):
    """ Calculate the Euclidean distance between two points (x, y). """
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

# Function to simulate pressing the spacebar key
def toggle_playback():
    pyautogui.press('space')  # Simulate pressing the spacebar key

# Create a context for hand detection with confidence thresholds
with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) as hands:
    last_toggle_time = 0
    toggle_interval = 1.0  # Time interval (in seconds) between toggles to avoid multiple activations

    while capture.isOpened():  # Continue while the webcam is open
        ret, frame = capture.read()  # Read a frame from the webcam
        if not ret:
            break  # Exit the loop if frame capture fails
        
        frame = cv2.flip(frame, 1)  # Flip the frame horizontally for mirror effect
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert the frame from BGR to RGB for MediaPipe
        detected_image = hands.process(image)  # Process the frame for hand detection
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # Convert back to BGR for OpenCV

        thumb_tips = []  # List to store thumb tip coordinates
        index_tips = []  # List to store index finger tip coordinates
        middle_tips = []  # List to store middle finger tip coordinates

        if detected_image.multi_hand_landmarks:  # Check if hands are detected
            for hand_lms in detected_image.multi_hand_landmarks:  # Iterate over each detected hand
                # Draw landmarks for each hand
                for id, lm in enumerate(hand_lms.landmark):  # Iterate over each landmark in the hand
                    h, w, c = image.shape  # Get image dimensions (height, width, channels)
                    cx, cy = int(lm.x * w), int(lm.y * h)  # Calculate (x, y) coordinates of the landmark
                    
                    # Draw a circle for each landmark
                    cv2.circle(image, (cx, cy), 7, (255, 0, 255), cv2.FILLED)  # Magenta circle

                    # Add landmark ID next to the circle
                    cv2.putText(image, str(id), (cx, cy - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)  # Green text
                    
                # Store coordinates for thumb, index, and middle finger tips
                thumb_tip = hand_lms.landmark[4]  # Thumb tip landmark (id 4)
                thumb_tip_coords = (int(thumb_tip.x * w), int(thumb_tip.y * h))  # Calculate (x, y) coordinates
                thumb_tips.append(thumb_tip_coords)  # Add thumb tip coordinates to list

                index_tip = hand_lms.landmark[8]  # Index finger tip landmark (id 8)
                index_tip_coords = (int(index_tip.x * w), int(index_tip.y * h))  # Calculate (x, y) coordinates
                index_tips.append(index_tip_coords)  # Add index tip coordinates to list

                middle_tip = hand_lms.landmark[12]  # Middle finger tip landmark (id 12)
                middle_tip_coords = (int(middle_tip.x * w), int(middle_tip.y * h))  # Calculate (x, y) coordinates
                middle_tips.append(middle_tip_coords)  # Add middle tip coordinates to list

                # Draw connections between landmarks
                mp_drawing.draw_landmarks(image, hand_lms,
                                          mp_hands.HAND_CONNECTIONS,
                                          landmark_drawing_spec=mp.solutions.drawing_utils.DrawingSpec(
                                              color=(255, 0, 255), thickness=4, circle_radius=2),  # Landmark drawing specifications
                                          connection_drawing_spec=mp.solutions.drawing_utils.DrawingSpec(
                                              color=(20, 180, 90), thickness=2, circle_radius=2)  # Connection drawing specifications
                                          )
        
        if len(thumb_tips) >= 1 and len(index_tips) >= 1 and len(middle_tips) >= 1:
            thumb_tip1 = thumb_tips[0]
            index_tip1 = index_tips[0]
            middle_tip1 = middle_tips[0]

            # Draw lines between thumb and index, and between thumb and middle finger
            cv2.line(image, thumb_tip1, index_tip1, (0, 255, 0), 2)  # Green line between thumb and index
            cv2.line(image, thumb_tip1, middle_tip1, (0, 0, 255), 2)  # Red line between thumb and middle

            # Calculate distances between thumb and index, and between thumb and middle
            distance_thumb_index = calculate_distance(thumb_tip1, index_tip1)
            distance_thumb_middle = calculate_distance(thumb_tip1, middle_tip1)
            
            # Display the calculated distances on the frame
            text_position_index = (image.shape[1] - 250, 30)  # Position text at the top-right
            text_position_middle = (image.shape[1] - 250, 60)  # Position text at the top-right

            cv2.putText(image, f'Dist. Thumb-Index: {distance_thumb_index:.2f}', text_position_index, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)  # Display distance between thumb and index
            cv2.putText(image, f'Dist. Thumb-Middle: {distance_thumb_middle:.2f}', text_position_middle, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)  # Display distance between thumb and middle

            # Check if the distance between thumb and index is less than or equal to 20
            # and the distance between thumb and middle is at least 80
            if distance_thumb_index <= 20 and distance_thumb_middle >= 80:
                current_time = time.time()
                if current_time - last_toggle_time > toggle_interval:
                    toggle_playback()  # Simulate pressing the spacebar key
                    last_toggle_time = current_time  # Update the last toggle time

        cv2.imshow('Webcam', image)  # Display the processed image in a window named 'Webcam'
        
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit the loop if 'q' is pressed
            break

capture.release()  # Release the webcam
cv2.destroyAllWindows()  # Close all OpenCV windows
