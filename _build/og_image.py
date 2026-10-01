# Renders _build/og-image.html to assets/og-image.png (1200x630) with headless Chrome or Edge.
# Usage: python _build/og_image.py   (needs a network connection for the Google Fonts)
import os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(HERE, "og-image.html")
OUT = os.path.join(ROOT, "assets", "og-image.png")

CANDIDATES = [
    os.environ.get("CHROME", ""),
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
    shutil.which("chromium-browser") or "",
]
chrome = next((c for c in CANDIDATES if c and os.path.exists(c)), None)
if not chrome:
    sys.exit("Chrome/Edge not found: set the CHROME environment variable to its path.")

url = "file:///" + SRC.replace("\\", "/").lstrip("/")
subprocess.run([
    chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
    "--window-size=1200,630", "--virtual-time-budget=5000", "--allow-file-access-from-files",
    f"--screenshot={OUT}", url,
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("wrote", OUT)
