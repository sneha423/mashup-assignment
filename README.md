# Mashup Assignment

This project implements the **Mashup** assignment using two programs:

1. A **command line script** that creates an audio mashup from YouTube.
2. A **Flask web app** that generates the mashup and emails it to the user as a ZIP file.

---

## 2. Installation
Create and activate a virtual environment (recommended).

Install dependencies:

bash
pip install -r requirements.txt

FFmpeg must be installed and on PATH (for pydub and yt-dlp).

## 3. Program 1 – CLI Mashup
Usage

Run from the project root:

```

bash
python 102303033.py "<SingerName>" <NumberOfVideos> <AudioDuration> <OutputFileName>

```
Example
```
bash
python 102303033.py "Arijit Singh" 12 25 mashup.mp3
```

Behavior

Downloads N YouTube videos for the given singer using yt-dlp.

Extracts audio, trims each track to the first Y seconds.

Concatenates all clips into a single output audio file.

Validates:

NumberOfVideos > 10

AudioDuration > 20

Prints clear error messages for wrong parameters or runtime errors.

## 4. Program 2 – Web Mashup Service
Run the Flask app from the project root:
```
bash
python -m webapp.app
```
Then open http://127.0.0.1:5000/ in a browser.

Form inputs

Singer name

Number of videos (> 10)

Duration per video in seconds (> 20)

Email address

Behavior

Starts a background job that:

Creates the mashup using the shared create_mashup function.

Zips the final audio file.

Sends the ZIP to the provided email using Flask-Mail.

The web page shows a progress bar and status messages while the mashup is being created.
Note: For Gmail, an app password is required with 2‑Step Verification enabled.


