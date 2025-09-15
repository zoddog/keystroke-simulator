#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import time
import sys

class KeystrokeSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Keystroke Simulator")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Variables
        self.countdown_active = False
        self.countdown_value = 5
        self.original_layout = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Text input label
        ttk.Label(main_frame, text="Enter text to simulate (max 1000 characters):").grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5)
        )
        
        # Text input area
        self.text_area = scrolledtext.ScrolledText(
            main_frame, 
            height=15, 
            width=70,
            wrap=tk.WORD
        )
        self.text_area.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Bind text change event for character limit
        self.text_area.bind('<KeyRelease>', self.on_text_change)
        self.text_area.bind('<Button-1>', self.on_text_change)
        
        # Character counter
        self.char_count_label = ttk.Label(main_frame, text="Characters: 0/1000")
        self.char_count_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        button_frame.columnconfigure(0, weight=1)
        
        # Start button
        self.start_button = ttk.Button(
            button_frame, 
            text="Start (5 seconds delay)", 
            command=self.start_simulation
        )
        self.start_button.grid(row=0, column=0, padx=(0, 10), pady=(0, 10))
        
        # Quit button
        quit_button = ttk.Button(button_frame, text="Quit", command=self.quit_app)
        quit_button.grid(row=0, column=1, pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready")
        self.status_label.grid(row=4, column=0, columnspan=2, sticky=tk.W)
        
    def on_text_change(self, event=None):
        # Get current text and limit to 1000 characters
        current_text = self.text_area.get("1.0", tk.END)[:-1]  # Remove trailing newline
        char_count = len(current_text)
        
        if char_count > 1000:
            # Truncate text to 1000 characters
            truncated_text = current_text[:1000]
            self.text_area.delete("1.0", tk.END)
            self.text_area.insert("1.0", truncated_text)
            char_count = 1000
            
        # Update character counter
        self.char_count_label.config(text=f"Characters: {char_count}/1000")
        
        # Change color if approaching limit
        if char_count > 950:
            self.char_count_label.config(foreground="red")
        elif char_count > 800:
            self.char_count_label.config(foreground="orange")
        else:
            self.char_count_label.config(foreground="black")
    
    def start_simulation(self):
        text_to_type = self.text_area.get("1.0", tk.END).strip()
        
        if not text_to_type:
            messagebox.showwarning("Warning", "Please enter some text to simulate.")
            return
            
        if self.countdown_active:
            return
            
        # Check if ydotool is available
        try:
            subprocess.run(['which', 'ydotool'], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "ydotool not found. Please install ydotool.")
            return
        
        # Start countdown in a separate thread
        self.countdown_active = True
        countdown_thread = threading.Thread(target=self.countdown_and_simulate, args=(text_to_type,))
        countdown_thread.daemon = True
        countdown_thread.start()
    
    def countdown_and_simulate(self, text_to_type):
        try:
            # Countdown
            for i in range(5, 0, -1):
                self.root.after(0, lambda i=i: self.update_countdown_ui(i))
                time.sleep(1)
                
            # Start simulation
            self.root.after(0, lambda: self.status_label.config(text="Simulating keystrokes..."))
            
            # Simulate keystrokes using ydotool
            self.simulate_keystrokes(text_to_type)
            
            # Reset UI
            self.root.after(0, self.reset_ui_after_simulation)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Simulation failed: {str(e)}"))
            self.root.after(0, self.reset_ui_after_simulation)
    
    def update_countdown_ui(self, count):
        self.start_button.config(text=f"Starting in {count}...", state="disabled")
        self.status_label.config(text=f"Starting simulation in {count} seconds...")
    
    def reset_ui_after_simulation(self):
        self.countdown_active = False
        self.start_button.config(text="Start (5 seconds delay)", state="normal")
        self.status_label.config(text="Simulation completed!")
        
        # Reset status after 3 seconds
        self.root.after(3000, lambda: self.status_label.config(text="Ready"))
    
    def get_current_keyboard_layout(self):
        """Get the current keyboard layout"""
        try:
            # Try to get current layout using gsettings (GNOME/Ubuntu)
            result = subprocess.run(
                ['gsettings', 'get', 'org.gnome.desktop.input-sources', 'current'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None
    
    def set_keyboard_layout(self, layout_index=None):
        """Set keyboard layout. If layout_index is None, sets to US layout (usually index 0)"""
        try:
            if layout_index is None:
                # Try to find and set US layout
                # First, let's get available layouts
                result = subprocess.run(
                    ['gsettings', 'get', 'org.gnome.desktop.input-sources', 'sources'],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    sources = result.stdout.strip()
                    # Look for US layout in the sources
                    if "'xkb', 'us'" in sources or "'xkb', 'us+" in sources:
                        # Set to first layout (assuming US is configured)
                        subprocess.run(
                            ['gsettings', 'set', 'org.gnome.desktop.input-sources', 'current', '0'],
                            capture_output=True
                        )
            else:
                # Restore original layout
                subprocess.run(
                    ['gsettings', 'set', 'org.gnome.desktop.input-sources', 'current', str(layout_index)],
                    capture_output=True
                )
        except Exception as e:
            print(f"Warning: Could not change keyboard layout: {e}")
    
    def simulate_keystrokes(self, text):
        original_layout_index = None
        try:
            # Save current keyboard layout
            current_layout = self.get_current_keyboard_layout()
            if current_layout:
                try:
                    original_layout_index = int(current_layout.replace('uint32 ', ''))
                except:
                    original_layout_index = None
            
            # Switch to US keyboard layout
            self.root.after(0, lambda: self.status_label.config(text="Switching to US keyboard layout..."))
            self.set_keyboard_layout(None)  # Set to US layout
            time.sleep(0.5)  # Give system time to switch
            
            # Use ydotool to simulate typing
            # We need to run with elevated privileges for ydotool to work properly on Wayland
            # Use pkexec instead of sudo for GUI applications
            cmd = ['pkexec', 'ydotool', 'type', '--delay', '10', text]
            
            # Run the command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                raise Exception(f"ydotool failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise Exception("Simulation timed out")
        except Exception as e:
            raise Exception(f"Failed to simulate keystrokes: {str(e)}")
        finally:
            # Always restore original keyboard layout
            if original_layout_index is not None:
                self.root.after(0, lambda: self.status_label.config(text="Restoring original keyboard layout..."))
                self.set_keyboard_layout(original_layout_index)
                time.sleep(0.3)
    
    def quit_app(self):
        if self.countdown_active:
            if messagebox.askyesno("Confirm", "Simulation is in progress. Are you sure you want to quit?"):
                self.root.quit()
        else:
            self.root.quit()

def main():
    root = tk.Tk()
    app = KeystrokeSimulator(root)
    
    # Handle window close event
    root.protocol("WM_DELETE_WINDOW", app.quit_app)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()