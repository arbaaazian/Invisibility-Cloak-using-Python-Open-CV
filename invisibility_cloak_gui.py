import cv2
import numpy as np
import time
import tkinter as tk
from tkinter import ttk
import threading
import sys
import os

class InvisibilityCloakGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Invisibility Cloak")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Set style
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 12))
        self.style.configure('TLabel', font=('Arial', 14))
        self.style.configure('TRadiobutton', font=('Arial', 12))
        
        # Variables
        self.color_var = tk.StringVar(value="red")
        self.running = False
        self.cap = None
        self.background = None
        self.thread = None
        
        # Create UI elements
        self.create_widgets()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Harry Potter's Invisibility Cloak", 
                               font=("Arial", 24, "bold"))
        title_label.pack(pady=10)
        
        # Description
        desc_text = """This application uses computer vision to create an invisibility cloak effect.
        1. Select a cloak color below
        2. Click 'Start' and move away from the camera view
        3. After background capture, put on your colored cloak
        4. Watch yourself disappear like magic!"""
        desc_label = ttk.Label(main_frame, text=desc_text, wraplength=700, 
                              justify="center", font=("Arial", 12))
        desc_label.pack(pady=20)
        
        # Color selection frame
        color_frame = ttk.LabelFrame(main_frame, text="Select Cloak Color", padding=10)
        color_frame.pack(pady=10, fill="x")
        
        # Color options
        colors = [("Gryffindor Red", "red"), 
                 ("Ravenclaw Blue", "blue"), 
                 ("Slytherin Green", "green")]
        
        for i, (color_name, color_value) in enumerate(colors):
            rb = ttk.Radiobutton(color_frame, text=color_name, value=color_value, 
                                variable=self.color_var)
            rb.grid(row=0, column=i, padx=30, pady=5, sticky="w")
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        # Start button
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_cloak, width=15)
        self.start_button.grid(row=0, column=0, padx=10)
        
        # Stop button
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_cloak, 
                                    width=15, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=10)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding=10)
        status_frame.pack(pady=10, fill="x")
        
        # Status label
        self.status_label = ttk.Label(status_frame, text="Ready to start", font=("Arial", 12))
        self.status_label.pack(pady=5)
        
        # Credits
        credits_label = ttk.Label(main_frame, text="Created with Python and OpenCV", 
                                font=("Arial", 10, "italic"))
        credits_label.pack(side="bottom", pady=10)
    
    def update_status(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def start_cloak(self):
        if self.running:
            return
        
        self.running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        # Start processing in a separate thread
        self.thread = threading.Thread(target=self.run_invisibility_cloak)
        self.thread.daemon = True
        self.thread.start()
    
    def stop_cloak(self):
        self.running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.update_status("Stopped")
        
        # Release resources
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
            cv2.destroyAllWindows()
    
    def on_closing(self):
        self.running = False
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        self.root.destroy()
        sys.exit(0)
    
    def get_background(self):
        self.update_status("Capturing background... Please move out of the frame.")
        
        # Allow the camera to warm up and adjust to lighting
        for i in range(30):
            ret, background = self.cap.read()
            if not ret:
                self.update_status("Failed to capture background.")
                return None
        
        self.update_status("Background captured successfully!")
        return background
    
    def get_color_bounds(self, color_name):
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
            self.update_status(f"Color {color_name} not supported. Using default red color.")
            lower_bounds = [np.array([0, 120, 70]), np.array([160, 120, 70])]
            upper_bounds = [np.array([10, 255, 255]), np.array([180, 255, 255])]
            return lower_bounds, upper_bounds, True
    
    def create_mask(self, frame, lower_bounds, upper_bounds, is_dual_range):
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
    
    def apply_invisibility_effect(self, frame, background, mask):
        # Invert the mask to get the region without the cloak
        mask_inv = cv2.bitwise_not(mask)
        
        # Use the mask to extract the foreground (person without cloak)
        foreground = cv2.bitwise_and(frame, frame, mask=mask_inv)
        
        # Use the inverted mask to extract the background for the cloak region
        background_cloak = cv2.bitwise_and(background, background, mask=mask)
        
        # Combine the foreground and the background for the cloak region
        result = cv2.add(foreground, background_cloak)
        
        return result
    
    def run_invisibility_cloak(self):
        # Open the webcam
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            self.update_status("Error: Could not open webcam.")
            self.running = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            return
        
        # Set camera resolution for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Get selected color
        selected_color = self.color_var.get()
        
        # Give the user time to move out of the frame
        self.update_status(f"Using {selected_color} as the invisibility cloak color.")
        self.update_status("Prepare for background capture in 5 seconds...")
        
        # Countdown
        for i in range(5, 0, -1):
            if not self.running:
                return
            self.update_status(f"Capturing background in {i} seconds...")
            time.sleep(1)
        
        # Capture the background
        self.background = self.get_background()
        if self.background is None:
            self.running = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            return
        
        # Get color bounds for the specified color
        lower_bounds, upper_bounds, is_dual_range = self.get_color_bounds(selected_color)
        
        self.update_status(f"Put on your {selected_color} cloak and step back into the frame.")
        
        # Main loop to process frames
        while self.running:
            # Read a frame from the webcam
            ret, frame = self.cap.read()
            
            if not ret:
                self.update_status("Failed to capture frame.")
                break
            
            # Create mask for the specified color
            mask = self.create_mask(frame, lower_bounds, upper_bounds, is_dual_range)
            
            # Apply the invisibility effect
            result = self.apply_invisibility_effect(frame, self.background, mask)
            
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
        if self.cap is not None and self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()

def main():
    root = tk.Tk()
    app = InvisibilityCloakGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()