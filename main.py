import threading
from pynput import keyboard
import pyautogui
import cv2
import numpy as np
import mss
import mss.tools
from PIL import Image


def take_screenshot(left, top, width, height):
    # Create an MSS instance
    with mss.mss() as sct:
        # Define the region to capture
        monitor = {"left": left, "top": top, "width": width, "height": height}

        # Capture the region
        screenshot = sct.grab(monitor)

        # Convert the screenshot to PIL Image
        img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

        # Return the screenshot as an image object
        return img


def calculate_y(y, x1, y1, x2, y2):
    # Calculate the slope 'm'
    if x2 - x1 != 0:
        m = (y2 - y1) / (x2 - x1)
    else:
        m = 1

    # Calculate the y-intercept 'b'
    b = y1 - m * x1

    # Calculate the position 'x' for the given 'y'
    if m != 0:
        x = (y - b) / m
    else:
        x = 320

    return x


def on_press(key):
    if key == keyboard.Key.esc:
        print('Escape key pressed. Exiting...')
        # Set a flag to indicate that the loop should be exited
        global exit_flag
        exit_flag = True
    elif key == keyboard.Key.up:
        print('Up arrow key pressed. Starting the bot...')
        # Set a flag to indicate that the loop should start
        global start_flag
        start_flag = True


# Create a listener for keystrokes
listener = keyboard.Listener(on_press=on_press)
# Start listening in a separate thread
listener_thread = threading.Thread(target=listener.start)
listener_thread.start()

# Load the reference image
reference_image = cv2.imread('ref.png')

# Get the reference image dimensions
ref_height, ref_width, _ = reference_image.shape

# Wait for the up arrow key to start the loop
start_flag = False
prv = 0
while not start_flag:
    pass

exit_flag = False
x1, y1 = 0, 0
x2, y2 = 0, 0

while not exit_flag:
    
    screen_image = take_screenshot(662, 203, 1263, 673)
    screen_image = cv2.cvtColor(np.array(screen_image), cv2.COLOR_RGB2BGR)

    # Find the reference image on the screen
    result = cv2.matchTemplate(
        screen_image, reference_image, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    # Get the coordinates of the reference image
    top_left = max_loc
    bottom_right = (top_left[0] + ref_width, top_left[1] + ref_height)

    # Get the center position of the reference image
    center_x = top_left[0] + ref_width // 2
    center_y = top_left[1] + ref_height // 2

    x2, y2 = x1, y1
    x1, y1 = center_x, center_y

    if y1 <= y2:
      #Follow the ball when it moves up
        target_x = center_x
    else:
      #Calculate X position for collision on y = 436
      #Go to calculation position when ball goes down
        target_x = calculate_y(436, x1, y1, x2, y2)
        print("calculated down ", int(target_x), "\t\t x1: ", x1, "\ty1: ", y1, " || ", " \t x2: ", x2, "\t y2: ", y2)

    # Move the mouse cursor to the center of the reference image
    pyautogui.moveTo(target_x+662, center_y+203)


cv2.destroyAllWindows()
# Stop the listener
listener.stop()
listener_thread.join()
