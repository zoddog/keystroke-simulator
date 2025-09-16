#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import time
import sys
import re

APP_VERSION = "v0.1.0"

class KeystrokeSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Keystroke Simulator {APP_VERSION}")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Variables
        self.countdown_active = False
        self.countdown_value = 5
        self.original_layout = None
        self.original_sources = None
        self.original_current_index = None
        self.language_var = tk.StringVar(value="HU")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Language selection frame
        lang_frame = ttk.LabelFrame(main_frame, text="Input Language", padding="5")
        lang_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Radiobutton(lang_frame, text="Hungarian (HU)", variable=self.language_var, value="HU").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(lang_frame, text="US English (US)", variable=self.language_var, value="US").pack(side=tk.LEFT)
        
        # Text input label
        ttk.Label(main_frame, text="Enter text to simulate (max 1000 characters):").grid(
            row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 5)
        )
        
        # Text input area
        self.text_area = scrolledtext.ScrolledText(
            main_frame, 
            height=15, 
            width=70,
            wrap=tk.WORD
        )
        self.text_area.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Bind text change event for character limit
        self.text_area.bind('<KeyRelease>', self.on_text_change)
        self.text_area.bind('<Button-1>', self.on_text_change)
        
        # Character counter
        self.char_count_label = ttk.Label(main_frame, text="Characters: 0/1000")
        self.char_count_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
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
        self.status_label.grid(row=5, column=0, columnspan=2, sticky=tk.W)
        
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
        # Get the text exactly as provided (no modifications), excluding Tk's trailing newline
        text_to_type = self.text_area.get("1.0", "end-1c")
        
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
        """Get the current keyboard layout index as string (e.g. 'uint32 0')"""
        try:
            result = subprocess.run(
                ['gsettings', 'get', 'org.gnome.desktop.input-sources', 'current'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def get_input_sources(self):
        """Get the current input sources string, e.g. "[('xkb', 'hu'), ('xkb', 'us')]"""
        try:
            result = subprocess.run(
                ['gsettings', 'get', 'org.gnome.desktop.input-sources', 'sources'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None

    def set_input_sources(self, sources_str: str):
        try:
            subprocess.run(
                ['gsettings', 'set', 'org.gnome.desktop.input-sources', 'sources', sources_str],
                capture_output=True, text=True
            )
        except Exception as e:
            print(f"Warning: Could not set input sources: {e}")

    def set_current_layout_index(self, index: int):
        try:
            subprocess.run(
                ['gsettings', 'set', 'org.gnome.desktop.input-sources', 'current', str(index)],
                capture_output=True, text=True
            )
        except Exception as e:
            print(f"Warning: Could not set current layout index: {e}")

    def ensure_us_layout(self):
        """Ensure that US layout is available and active. Save originals for restoration.
        Returns the index of the US layout after adjustment.
        """
        self.original_sources = self.get_input_sources()
        current_s = self.get_current_keyboard_layout()
        try:
            self.original_current_index = int(current_s.replace('uint32 ', '')) if current_s else None
        except Exception:
            self.original_current_index = None

        sources = self.original_sources or "[]"
        # Parse layout codes
        layouts = re.findall(r"\('xkb', '([^']+)'\)", sources)
        if not layouts:
            layouts = []

        if 'us' not in layouts:
            # Prepend 'us' to sources
            new_layouts = ['us'] + layouts
            inside = ", ".join(["('xkb', '%s')" % l for l in new_layouts])
            new_sources = f"[{inside}]"
            self.set_input_sources(new_sources)
            us_index = 0
        else:
            us_index = layouts.index('us')

        # Activate US layout
        self.set_current_layout_index(us_index)
        return us_index

    def restore_original_layout(self):
        try:
            if self.original_sources is not None:
                self.set_input_sources(self.original_sources)
            if self.original_current_index is not None:
                self.set_current_layout_index(self.original_current_index)
        except Exception as e:
            print(f"Warning: Could not restore original layout: {e}")
    
    def convert_hungarian_to_us(self, text):
        """Convert Hungarian keyboard input to US keyboard mapping"""
        # Hungarian to US character mapping
        hu_to_us_map = {
            # Numbers row special characters
            '§': '`',     # section sign to backtick
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '0': '0',
            'ö': '-',     # ö to minus
            'ü': '=',     # ü to equals
            'Ö': '_',     # Ö to underscore
            'Ü': '+',     # Ü to plus
            # Additional underscore mappings  
            '_': '_',     # underscore to underscore (direct)
            'ß': '_',     # German ß sometimes maps to underscore
            
            # Shift+number combinations on Hungarian keyboard
            '\'': '!',    # Shift+1 on HU keyboard
            '"': '@',     # Shift+2 on HU keyboard  
            '+': '#',     # Shift+3 on HU keyboard
            '!': '$',     # Shift+4 on HU keyboard
            '%': '%',     # Shift+5 on HU keyboard
            '/': '^',     # Shift+6 on HU keyboard
            '=': '&',     # Shift+7 on HU keyboard
            '(': '*',     # Shift+8 on HU keyboard
            ')': '(',     # Shift+9 on HU keyboard
            # But we also need direct mappings
            '@': '@',     # at symbol direct
            '#': '#',     # hash direct
            
            # Top row
            'q': 'q',
            'w': 'w',
            'e': 'e',
            'r': 'r',
            't': 't',
            'z': 'y',     # Hungarian z to US y
            'u': 'u',
            'i': 'i',
            'o': 'o',
            'p': 'p',
            'ő': '[',     # ő to left bracket
            'ú': ']',     # ú to right bracket
            'Ő': '{',     # Ő to left brace
            'Ú': '}',     # Ú to right brace
            
            # Middle row
            'a': 'a',
            's': 's',
            'd': 'd',
            'f': 'f',
            'g': 'g',
            'h': 'h',
            'j': 'j',
            'k': 'k',
            'l': 'l',
            'é': ';',     # é to semicolon
            'á': "'",    # á to apostrophe
            'É': ':',     # É to colon
            'Á': '"',     # Á to quotation mark
            # Additional quote mappings
            '"': '"',     # double quote direct
            "'": "'",    # single quote direct
            
            # Bottom row
            'y': 'y',     # keep y as y (we ensure US layout separately)
            'x': 'x',
            'c': 'c',
            'v': 'v',
            'b': 'b',
            'n': 'n',
            'm': 'm',
            'z': 'z',     # keep z as z (no swap)
            ',': ',',
            '.': '.',
            '-': '-',     # dash to dash (keep direct)
            '/': '/',     # slash direct
            '?': '?',
            
            # Special characters that need shift
            '!': '!',     # exclamation
            '@': '@',     # at symbol
            '#': '#',     # hash
            '$': '$',     # dollar
            '%': '%',     # percent
            '^': '^',     # caret
            '&': '&',     # ampersand
            '*': '*',     # asterisk
            '(': '(',     # left parenthesis
            ')': ')',     # right parenthesis
            
            # Common punctuation
            ' ': ' ',     # space
            '\t': '\t',   # tab
            '\n': '\n',   # newline
            '\r': '\r',   # carriage return
            
            # Pipe and backslash
            'í': '\\',    # í to backslash
            'Í': '|',     # Í to pipe
            '|': '|',     # pipe direct
            '\\': '\\',   # backslash direct
            
            # Additional common mappings that might be missed
            'ű': '[',     # ű to left bracket (alternative)
            'Ű': '{',     # Ű to left brace (alternative)
            
            # AltGr combinations that produce special characters on Hungarian keyboard
            '~': '~',     # tilde
            '`': '`',     # backtick
            '^': '^',     # caret
        }
        
        if self.language_var.get() == "HU":
            # Convert Hungarian input to US mapping
            converted = ""
            for char in text:
                converted += hu_to_us_map.get(char, char)
            return converted
        else:
            # US input, no conversion needed
            return text
    
    def simulate_keystrokes(self, text):
        original_layout_index = None
        try:
            # Ensure US keyboard layout is active; save originals for restoration
            self.root.after(0, lambda: self.status_label.config(text="Switching to US keyboard layout..."))
            self.ensure_us_layout()
            time.sleep(0.5)  # Give system time to switch
            
            # Convert text based on selected language
            converted_text = self.convert_hungarian_to_us(text)
            
            # Use ydotool to simulate typing
            # We need to run with elevated privileges for ydotool to work properly on Wayland
            # Use pkexec with a small delay after auth so focus can return to the target window
            # Pass text via env var to avoid shell-quoting issues
            cmd = [
                'pkexec', 'env', f'TYPETEXT={converted_text}',
                'sh', '-c', 'sleep 3; ydotool type --delay 10 -- "$TYPETEXT"'
            ]
            
            # Run the command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                raise Exception(f"ydotool failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise Exception("Simulation timed out")
        except Exception as e:
            raise Exception(f"Failed to simulate keystrokes: {str(e)}")
        finally:
            # Always restore original keyboard layout and sources
            self.root.after(0, lambda: self.status_label.config(text="Restoring original keyboard layout..."))
            self.restore_original_layout()
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