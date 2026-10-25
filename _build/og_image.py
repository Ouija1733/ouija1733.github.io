# Renders the preview images with headless Chrome or Edge:
#   _build/og-image.html         -> assets/og-image.png (1200x630, Open Graph)
#   _build/apple-touch-icon.html -> assets/apple-touch-icon.png (180x180, home-screen icon)
# Usage: python _build/og_image.py   (fonts are local, no network needed)
import os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
JOBS = [
    ("og-image.html", "og-image.png", (1200, 630)),
    ("apple-touch-icon.html", "apple-touch-icon.png", (180, 180)),
]

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

for src, out, (w, h) in JOBS:
    url = "file:///" + os.path.join(HERE, src).replace("\\", "/").lstrip("/")
    dest = os.path.join(ROOT, "assets", out)
    subprocess.run([
        chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
        f"--window-size={w},{h}", "--virtual-time-budget=5000", "--allow-file-access-from-files",
        f"--screenshot={dest}", url,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("wrote", dest)
