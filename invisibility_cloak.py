import cv2
import numpy as np
import time
import argparse

def get_background(cap):
    """
    Function to capture the background image without any person or object in the frame.
    """
    print("Capturing background...")
    print("Please move out of the frame for background capture.")
    
    # Allow the camera to warm up and adjust to lighting
    for i in range(30):
        ret, background = cap.read()
        if not ret:
            print("Failed to capture background.")
            exit(1)
    
    print("Background captured successfully!")
    return background

def get_color_bounds(color_name):
    """
    Function to get the HSV color bounds for the specified color.
    """
    if color_name.lower() == 'red':
        # Red has two ranges in HSV
        lower_bounds = [np.array([0, 120, 70]), np.array([160, 120, 70])]
        upper_bounds = [np.array([10, 255, 255]), np.array([180, 255, 255])]
        return lower_bounds, upper_bounds, True  # True indicates dual range
    
    elif color_name.lower() == 'blue':
        lower_bound = np.array([100, 120, 70])
        upper_bound = np.array([140, 255, 255])
        return [lower_bound], [upper_bound], False
    
    elif color_name.lower() == 'green':
        lower_bound = np.array([40, 120, 70])
        upper_bound = np.array([80, 255, 255])
        return [lower_bound], [upper_bound], False
    
    else:
        print(f"Color {color_name} not supported. Using default red color.")
        lower_bounds = [np.array([0, 120, 70]), np.array([160, 120, 70])]
        upper_bounds = [np.array([10, 255, 255]), np.array([180, 255, 255])]
        return lower_bounds, upper_bounds, True

def create_mask(frame, lower_bounds, upper_bounds, is_dual_range):
    """
    Function to create a mask for the specified color range(s).
    """
    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Initialize mask
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    
    if is_dual_range:
        # For colors like red that wrap around the HSV color space
        for i in range(len(lower_bounds)):
            temp_mask = cv2.inRange(hsv, lower_bounds[i], upper_bounds[i])
            mask = cv2.bitwise_or(mask, temp_mask)
    else:
        # For colors with a single range
        mask = cv2.inRange(hsv, lower_bounds[0], upper_bounds[0])
    
    # Noise removal
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8), iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, np.ones((3, 3), np.uint8), iterations=1)
    
    return mask

def apply_invisibility_effect(frame, background, mask):
    """
    Function to apply the invisibility effect using the mask.
    """
    # Invert the mask to get the region without the cloak
    mask_inv = cv2.bitwise_not(mask)
    
    # Use the mask to extract the foreground (person without cloak)
    foreground = cv2.bitwise_and(frame, frame, mask=mask_inv)
    
    # Use the inverted mask to extract the background for the cloak region
    background_cloak = cv2.bitwise_and(background, background, mask=mask)
    
    # Combine the foreground and the background for the cloak region
    result = cv2.add(foreground, background_cloak)
    
    return result

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Invisibility Cloak using OpenCV')
    parser.add_argument('--color', type=str, default='red', 
                        help='Color of the cloak (red, blue, or green)')
    args = parser.parse_args()
    
    # Open the webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit(1)
    
    # Set camera resolution for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Give the user time to move out of the frame
    print(f"Using {args.color} as the invisibility cloak color.")
    print("Prepare for background capture in 5 seconds...")
    time.sleep(5)
    
    # Capture the background
    background = get_background(cap)
    
    # Get color bounds for the specified color
    lower_bounds, upper_bounds, is_dual_range = get_color_bounds(args.color)
    
    print(f"Put on your {args.color} cloak and step back into the frame.")
    print("Press 'q' to quit the application.")
    
    # Main loop to process frames
    while True:
        # Read a frame from the webcam
        ret, frame = cap.read()
        
        if not ret:
            print("Failed to capture frame.")
            break
        
        # Create mask for the specified color
        mask = create_mask(frame, lower_bounds, upper_bounds, is_dual_range)
        
        # Apply the invisibility effect
        result = apply_invisibility_effect(frame, background, mask)
        
        # Display the original frame
        cv2.imshow('Original', frame)
        
        # Display the mask
        cv2.imshow('Mask', mask)
        
        # Display the result with invisibility effect
        cv2.imshow('Invisibility Cloak', result)
        
        # Check for user input to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()