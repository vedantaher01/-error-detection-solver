import os
import re

import cv2
import numpy as np
import pytesseract
from PIL import Image

# Point pytesseract to the Tesseract program (only if it exists at this path)
_TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(_TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = _TESSERACT_PATH


def preprocess_image(image):
    """Convert a PIL image into a clean black-and-white image for OCR."""
    img = np.array(image.convert("RGB"))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Enlarge small images so the digits are easier to read
    height, width = img.shape[:2]
    scale = 2.0 if width < 1200 else 1.5 if width < 2000 else 1.0
    if scale != 1.0:
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # Grayscale, smooth noise, then black/white threshold
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 9, 75, 75)
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    return gray


def _fix_binary_lookalikes(text):
    """Inside bit strings, turn O/o into 0 and l/I into 1.
    Only touches tokens of 4+ characters that are mostly real 0/1 digits,
    so normal words (like 'loll' or 'Hello') are left alone."""

    def repl(match):
        token = match.group(0)
        real_digits = sum(c in "01" for c in token)
        if real_digits >= 2 and real_digits >= len(token) / 2:
            return (token.replace("O", "0").replace("o", "0")
                         .replace("l", "1").replace("I", "1"))
        return token

    return re.sub(r"(?<![A-Za-z0-9])[01OolI]{4,}(?![A-Za-z0-9])", repl, text)


def extract_text_from_image(image):
    processed = preprocess_image(image)
    text = pytesseract.image_to_string(processed, config="--psm 6")
    text = _fix_binary_lookalikes(text.strip())
    return text