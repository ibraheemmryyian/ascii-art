import soundcard as sc
import numpy as np
import sys
import tkinter as tk
import threading

# Configuration
SAMPLE_RATE = 44100
BLOCK_SIZE = 2048
MAX_FREQ = 8000
WIDGET_COLS = 60
WIDGET_LINES = 12

latest_block = np.zeros(BLOCK_SIZE)
smoothed_mags = None

def audio_loop(app):
    global latest_block
    try:
        # Capture system audio loopback (what the speakers are emitting)
        spk = sc.default_speaker()
        m = sc.get_microphone(id=str(spk.name), include_loopback=True)
        with m.recorder(samplerate=SAMPLE_RATE) as mic:
            while app.running:
                data = mic.record(numframes=BLOCK_SIZE)
                if len(data.shape) > 1 and data.shape[1] > 0:
                    # Take first channel (left)
                    latest_block = data[:, 0].copy()
                else:
                    latest_block = data.flatten().copy()
    except Exception as e:
        print("Audio Thread Error:", e)

class AudioWidget(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.running = True
        
        # Window setup
        self.overrideredirect(True) # Borderless
        
        # 0.6 alpha gives a nice frosted glass see-through effect
        self.wm_attributes("-alpha", 0.65) 
        self.configure(bg='#1E1E2E') # Dark slate background instead of pure black
        
        # Position at the bottom-left corner above taskbar
        self.geometry("+20-60")
        
        # Push behind other windows
        self.lower()
        
        # ASCII Display Label
        self.label = tk.Label(
            self, 
            text="", 
            font=("Consolas", 10, "bold"), 
            fg="#00FFFF", # Bright cyan for maximum contrast
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
        
        # Start audio capture thread
        self.audio_thread = threading.Thread(target=audio_loop, args=(self,), daemon=True)
        self.audio_thread.start()
            
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
        global latest_block, smoothed_mags
        
        if not self.running:
            return
            
        max_height = WIDGET_LINES
        cols = WIDGET_COLS
        
        window = np.hanning(len(latest_block))
        fft_result = np.fft.rfft(latest_block * window)
        fft_freqs = np.fft.rfftfreq(len(latest_block), 1.0 / SAMPLE_RATE)
        
        valid_indices = fft_freqs <= MAX_FREQ
        fft_result = fft_result[valid_indices]
        magnitude = np.abs(fft_result)
        
        num_bins = cols
        if num_bins > len(magnitude): 
            num_bins = len(magnitude)

        if num_bins > 0:
            bin_splits = np.array_split(magnitude, num_bins)
            binned_mags = np.array([np.mean(b) if len(b) > 0 else 0 for b in bin_splits])
            
            if smoothed_mags is None or len(smoothed_mags) != len(binned_mags):
                smoothed_mags = binned_mags
            else:
                smoothed_mags = smoothed_mags * 0.6 + binned_mags * 0.4
                
            max_val = np.max(smoothed_mags)
            if max_val < 0.1: 
                max_val = 0.1
            
            normalized = smoothed_mags / max_val
            normalized = np.power(normalized, 0.6) 
            
            bar_heights = np.clip(np.int_(normalized * max_height), 0, max_height)
            
            out_lines = []
            for h in range(max_height, 0, -1):
                line = ""
                for bar_h in bar_heights:
                    if bar_h >= h:
                        if h > max_height * 0.8:
                            line += '@'
                        elif h > max_height * 0.4:
                            line += '#'
                        else:
                            line += ':'
                    else:
                        line += ' '
                out_lines.append(line)
            
            ascii_art = '\n'.join(out_lines)
            self.label.config(text=ascii_art)
            
        # Schedule next update (~25 FPS = 40ms)
        self.after(40, self.update_visualizer)

if __name__ == "__main__":
    app = AudioWidget()
    app.mainloop()
