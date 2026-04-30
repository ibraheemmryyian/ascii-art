import cv2
import numpy as np
import tkinter as tk
import threading

# Configuration for a MUCH bigger and more detailed view
# We use a higher resolution to capture face details
WIDGET_COLS = 160
WIDGET_LINES = 60

# High-contrast ASCII palette
ASCII_CHARS = " .':-+=*#%@"

latest_frame = None

def camera_loop(app):
    global latest_frame
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
        
    try:
        # Initialize CLAHE for better local contrast (makes faces pop)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        
        while app.running:
            ret, frame = cap.read()
            if not ret:
                continue
                
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Flip horizontally for a mirror effect
            gray = cv2.flip(gray, 1)
            
            # Apply CLAHE to significantly boost contrast and reveal facial features
            gray = clahe.apply(gray)
            
            # Optionally sharpen the image slightly
            # kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            # gray = cv2.filter2D(gray, -1, kernel)
            
            # Resize to our large ASCII grid
            resized = cv2.resize(gray, (WIDGET_COLS, WIDGET_LINES))
            
            latest_frame = resized.copy()
            
    except Exception as e:
        print("Camera Thread Error:", e)
    finally:
        cap.release()

class CameraApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.running = True
        self.title("ASCII Face Tracker Pro")
        
        # NOT a widget - standard windowed mode for "for fun" usage
        self.configure(bg='black')
        
        # Set a reasonable initial size but allow resizing
        self.geometry("1200x900")
        
        # Use a Text widget for high-performance rendering of large ASCII blocks
        self.text_area = tk.Text(
            self,
            font=("Consolas", 7, "bold"),
            fg="#00FFFF", # High-contrast Cyan
            bg="black",
            borderwidth=0,
            highlightthickness=0
        )
        self.text_area.pack(expand=True, fill='both')
        
        # Start camera capture thread
        self.camera_thread = threading.Thread(target=camera_loop, args=(self,), daemon=True)
        self.camera_thread.start()
            
        # Start GUI update loop
        self.update_visualizer()

    def close_widget(self):
        self.running = False
        self.destroy()

    def update_visualizer(self):
        global latest_frame
        
        if not self.running:
            return
            
        if latest_frame is not None:
            # Map pixels to ASCII
            ascii_frame = []
            for row in latest_frame:
                line = "".join([ASCII_CHARS[int((pixel / 255.0) * (len(ASCII_CHARS) - 1))] for pixel in row])
                ascii_frame.append(line)
            
            full_frame = "\n".join(ascii_frame)
            
            # Update the text widget content
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert('1.0', full_frame)
            
        # Schedule next update (~20 FPS = 50ms)
        self.after(50, self.update_visualizer)

if __name__ == "__main__":
    app = CameraApp()
    app.protocol("WM_DELETE_WINDOW", app.close_widget)
    app.mainloop()
