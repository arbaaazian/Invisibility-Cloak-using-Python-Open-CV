# Invisibility Cloak using OpenCV 🧙‍♂️✨

This project is inspired by Harry Potter's cloak of invisibility, but instead of wizardry, it uses computer vision to make parts of you disappear on camera.

## 🔍 How it Works

1. **Background Capture** → The program first records a static background (the scene without you in it).
2. **Color Detection** → When you wear a cloak of a specific color (red, blue, or green), OpenCV detects those pixels in each frame using HSV color space.
3. **Masking** → Those cloak-colored regions are masked and replaced with the pre-recorded background.
4. **Result** → Everything except the cloak is visible, making it look like you vanished.

## 🛠 Tech Behind It

- **Python** → Main language
- **OpenCV** → For real-time image processing (color detection, masking, blending)
- **NumPy** → For fast matrix operations on image frames
- **Tkinter** → For the graphical user interface (GUI version only)

## 📋 Requirements

```
opencv-python
numpy
tkinter (included with Python)
```

You can install the required packages using pip:

```bash
pip install opencv-python numpy
```

## 🚀 Usage

### Command Line Version

Run the command line version with:

```bash
python invisibility_cloak.py --color red
```

You can specify the color of your cloak with the `--color` argument. Options are:
- `red` (default)
- `blue`
- `green`

### GUI Version

For a more user-friendly experience, run the GUI version:

```bash
python invisibility_cloak_gui.py
```

The GUI allows you to:
- Select your cloak color (Gryffindor Red, Ravenclaw Blue, or Slytherin Green)
- Start and stop the invisibility effect with buttons
- See status updates

## 📝 Instructions

1. Run the application
2. Move away from the camera view for background capture
3. Put on a cloth/cloak of the selected color
4. Step back into the frame and watch the magic happen!
5. Press 'q' to quit (command line version) or use the Stop button (GUI version)

## 🧪 How to Experiment

- Try different colors for your cloak
- Adjust lighting conditions for better detection
- Modify the HSV color ranges in the code to fine-tune detection for your specific cloth color

## 🤩 Why It's Cool

- Fun, beginner-friendly computer vision project
- Combines pop culture (Harry Potter) with tech
- Great way to learn image segmentation, masking, and video frame processing
- Customizable with multiple cloak colors

## 📸 Screenshots

(Add screenshots of your application in action here)

## 📜 License

This project is open source and available under the MIT License.
