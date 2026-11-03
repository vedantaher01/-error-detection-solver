# Error Detection Solver

Scan or upload a computer-networks problem and get a **step-by-step solution you can learn from**,
not just an answer. Supports Parity, Checksum, CRC and Hamming codes.

![Demo](docs/demo.png)

**[Try the live demo](YOUR-STREAMLIT-LINK)** (add this after Part 5)

## Why I built this
When I studied error detection, I could find answers online but not explanations I could repeat
in an exam. This app shows every step, a verification and common exam mistakes.

## Features
- Upload an image or use your camera (OCR with Tesseract + OpenCV)
- Automatically detects the method: Parity, Checksum, CRC, Hamming
- Teaching-style output: concept, worked steps, verification, exam tips
- Editable OCR text, so you can fix a misread digit before solving

## How it works
Image → OpenCV preprocessing → Tesseract OCR → method detection → rule-based solver → explanation

1. `ocr_utils.py`: cleans the image and extracts text
2. `solver.py`: detects the method and solves it with exact algorithms (no guessing)
3. `app.py`: Streamlit interface

## Run it locally
1. Install [Python 3.12+](https://www.python.org/downloads/) and [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
2. Clone and install:
```
git clone https://github.com/USERNAME/error-detection-solver.git
cd error-detection-solver
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Example problem
> A sender transmits the 7-bit data 1011001 using even parity. Find the parity bit and the
> transmitted codeword. At the receiver, the word 10110111 arrives. Is an error detected?

The app finds the parity bit `0`, codeword `10110010`, and explains why the 2-bit error goes undetected.

## Known limitations
- Works best with printed or typed text; handwriting is unreliable
- Problems must contain bit strings of 4+ digits
- Rule-based, so unusual wording may not be detected

## Roadmap
- [ ] 2D parity and Internet checksum (hex)
- [ ] Practice mode that generates new problems
- [ ] Handwriting support

## License
MIT
