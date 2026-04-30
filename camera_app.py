import cv2
import numpy as np
import tkinter as tk
import threading

# Configuration for the view - these will now be updated dynamically
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
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        
        while app.running:
            ret, frame = cap.read()
            if not ret:
                continue
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.flip(gray, 1)
            gray = clahe.apply(gray)
            
            # Use current dynamic dimensions
            current_cols = WIDGET_COLS
            current_lines = WIDGET_LINES
            
            if current_cols > 0 and current_lines > 0:
                resized = cv2.resize(gray, (current_cols, current_lines))
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
        self.configure(bg='black')
        self.geometry("1000x800")
        
        # Use a Text widget for high-performance rendering
        self.text_area = tk.Text(
            self,
            font=("Consolas", 7, "bold"),
            fg="#FFFFFF", # High-contrast White
            bg="black",
            borderwidth=0,
            highlightthickness=0
        )
        self.text_area.pack(expand=True, fill='both')
        
        # Bind the resize event
        self.bind("<Configure>", self.on_resize)
        
        # Start camera capture thread
        self.camera_thread = threading.Thread(target=camera_loop, args=(self,), daemon=True)
        self.camera_thread.start()
            
        # Start GUI update loop
        self.update_visualizer()

    def on_resize(self, event):
        global WIDGET_COLS, WIDGET_LINES
        
        # Get window dimensions
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Approximate character dimensions for Consolas 7pt bold
        # Width: ~5px, Height: ~12px
        char_w = 6
        char_h = 12
        
        # Calculate new grid size
        new_cols = max(10, width // char_w)
        new_lines = max(10, height // char_h)
        
        if new_cols != WIDGET_COLS or new_lines != WIDGET_LINES:
            WIDGET_COLS = new_cols
            WIDGET_LINES = new_lines

    def close_widget(self):
        self.running = False
        self.destroy()

    def update_visualizer(self):
        global latest_frame
        
        if not self.running:
            return
            
        if latest_frame is not None:
            # Match current frame dimensions
            # Map pixels to ASCII
            ascii_frame = []
            for row in latest_frame:
                line = "".join([ASCII_CHARS[int((pixel / 255.0) * (len(ASCII_CHARS) - 1))] for pixel in row])
                ascii_frame.append(line)
            
            full_frame = "\n".join(ascii_frame)
            
            # Update the text widget content
            self.text_area.delete('1.0', tk.END)
            self.text_area.insert('1.0', full_frame)
            
        # Schedule next update
        self.after(50, self.update_visualizer)

if __name__ == "__main__":
    app = CameraApp()
    app.protocol("WM_DELETE_WINDOW", app.close_widget)
    app.mainloop()
