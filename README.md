# Keystroke Simulator (AppImage)

Simple GUI to type a block of text into another application window (e.g., a browser-based terminal) on Ubuntu Wayland using ydotool. The text box accepts up to 1000 characters, provides a 5-second countdown, and then types the text quickly (no human-like delay). A Quit button is provided to close the app.

## Important tip for Dockge Terminal users
- If you want to send a bash command into Dockge Terminal, prepend 10–20 spaces before your command in the app’s text box. This improves reliability so the whole command reaches the terminal intact.

## Status and caveats
- This is a minimal, experimental tool. It’s bugged and not perfect; behavior can vary depending on focus, Wayland compositor, and the target app. Contributions to improve it are welcome.
- Typing relies on `ydotool` executed with elevated privileges (via `pkexec`). You may be prompted for your password.
- Keyboard layout is temporarily set to US during typing and then restored.
- In general, it’s not a great idea to use Dockge’s built‑in terminal for heavy interaction.

## Run
- Use the AppImage generated in this repository: `./Keystroke_Simulator-x86_64.AppImage`

## License
MIT
