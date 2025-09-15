# Keystroke Simulator

## Overview
A simple GUI application for simulating keystrokes on Ubuntu Wayland systems. Designed specifically for typing into applications that don't accept paste operations (like certain terminal interfaces in Docker/Dockge environments).

## Features
- Simple text input interface (max 1000 characters)
- 5-second countdown before typing begins
- Automatic keyboard layout switching (Hungarian to US and back)
- Fast keystroke simulation using ydotool
- AppImage distribution for easy deployment

## Technical Details
- **Platform**: Ubuntu Linux with Wayland
- **GUI Framework**: tkinter (Python standard library)
- **Keystroke Engine**: ydotool (requires elevated privileges)
- **Privilege Management**: pkexec for GUI password prompts
- **Layout Switching**: gsettings (GNOME/Ubuntu desktop)

## Current Issues
- Character mapping between Hungarian and US keyboard layouts needs refinement
- Some special characters may not map correctly during layout switching

## Usage
1. Run the AppImage: `./Keystroke_Simulator-x86_64.AppImage`
2. Enter text to simulate
3. Click "Start" and wait for 5-second countdown
4. Application will switch to US layout, type the text, then restore original layout

## Repository
https://github.com/zoddog/keystroke-simulator