import cv2
import numpy as np
import tkinter as tk
import threading

# Configuration
# Terminals characters are taller than they are wide. A typical ratio is 1:2.
# So if we want a squarish looking frame, width should be about 2x the height.
WIDGET_COLS = 90
WIDGET_LINES = 40

# 10 levels of density. Dark background = space for dark pixels, @ for bright pixels.
ASCII_CHARS = " .:-=+*#%@"

latest_frame = None

def camera_loop(app):
    global latest_frame
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
        
    try:
        while app.running:
            ret, frame = cap.read()
            if not ret:
                continue
                
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Flip horizontally for a mirror effect (feels more natural for webcams)
            gray = cv2.flip(gray, 1)
            
            # Resize. We ignore aspect ratio strictly and fit it into our grid.
            resized = cv2.resize(gray, (WIDGET_COLS, WIDGET_LINES))
            
            latest_frame = resized.copy()
            
    except Exception as e:
        print("Camera Thread Error:", e)
    finally:
        cap.release()

class CameraWidget(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.running = True
        
        # Window setup
        self.overrideredirect(True) # Borderless
        
        # 0.65 alpha gives a nice frosted glass see-through effect
        self.wm_attributes("-alpha", 0.65) 
        self.configure(bg='#1E1E2E')
        
        # Position at the top-right corner
        self.geometry("-20+20")
        
        # Push behind other windows
        self.lower()
        
        # ASCII Display Label
        self.label = tk.Label(
            self, 
            text="Initializing Camera...", 
            font=("Consolas", 7, "bold"), # Smaller font for high-res ASCII
            fg="#89DCEB", # Pastel cyan
            bg="#1E1E2E",
            justify="left",
            padx=15,
            pady=15
        )
        self.label.pack()
        
        # Mouse Dragging State
        self.offset_x = 0
        self.offset_y = 0
        
        # Bindings
        self.bind("<Button-1>", self.click_window)
        self.bind("<B1-Motion>", self.drag_window)
        self.bind("<Double-Button-1>", self.close_widget)
        
        # Start camera capture thread
        self.camera_thread = threading.Thread(target=camera_loop, args=(self,), daemon=True)
        self.camera_thread.start()
            
        # Start GUI update loop
        self.update_visualizer()

    def click_window(self, event):
        self.offset_x = event.x
        self.offset_y = event.y

    def drag_window(self, event):
        x = self.winfo_pointerx() - self.offset_x
        y = self.winfo_pointery() - self.offset_y
        self.geometry(f"+{x}+{y}")

    def close_widget(self, event):
        self.running = False
        self.destroy()

    def update_visualizer(self):
        global latest_frame
        
        if not self.running:
            return
            
        if latest_frame is not None:
            # Map pixels to ASCII
            ascii_frame = ""
            for row in latest_frame:
                line = ""
                for pixel in row:
                    # pixel is 0-255
                    idx = int((pixel / 255.0) * (len(ASCII_CHARS) - 1))
                    line += ASCII_CHARS[idx]
                ascii_frame += line + "\n"
                
            self.label.config(text=ascii_frame)
            
        # Schedule next update (~20 FPS = 50ms)
        self.after(50, self.update_visualizer)

if __name__ == "__main__":
    app = CameraWidget()
    app.mainloop()
