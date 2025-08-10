import os
import sys
import threading
import time
import webbrowser
from app import app


def open_browser():
    """Wait for server to start then open browser"""
    time.sleep(2)  # Wait for Flask to start
    webbrowser.open('http://127.0.0.1:5000')


def resource_path(relative_path):
    """Get absolute path to resource for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


if __name__ == '__main__':
    # Start browser in separate thread
    threading.Thread(target=open_browser).start()

    # Run Flask app
    print("Starting Intelligent Workout Planner...")
    print("The browser will open automatically...")
    print("To stop the server, close this window")

    app.run(debug=False, port=5000, use_reloader=False)
