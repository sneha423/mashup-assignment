import os
import re
import zipfile
import threading
from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message  # [web:8][web:27]

from mashup_core.mashup import create_mashup

app = Flask(__name__)

# Configure mail (example: Gmail SMTP; use app password, not plain password). [web:8][web:27]
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = "sgupta10_be23@thapar.edu"       # TODO: change
app.config["MAIL_PASSWORD"] = "ztqqtguphhxtkctn"     # 
app.config["MAIL_DEFAULT_SENDER"] = app.config["MAIL_USERNAME"]

mail = Mail(app)


# Global progress state (simple, one job at a time)
progress_state = {
    "percent": 0,
    "message": "",
    "done": False,
    "error": None,
}
progress_lock = threading.Lock()


def reset_progress():
    with progress_lock:
        progress_state["percent"] = 0
        progress_state["message"] = ""
        progress_state["done"] = False
        progress_state["error"] = None


def is_valid_email(email: str) -> bool:
    """
    Basic email format validation. [file:1]
    """
    pattern = r"^[^@]+@[^@]+\.[^@]+$"
    return re.match(pattern, email) is not None


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    message = None

    if request.method == "POST":
        singer = request.form.get("singer", "").strip()
        num_videos_str = request.form.get("num_videos", "").strip()
        duration_str = request.form.get("duration", "").strip()
        email = request.form.get("email", "").strip()

        # Validate fields
        if not singer:
            error = "Singer name is required."
            return render_template("index.html", error=error, message=message)

        try:
            num_videos = int(num_videos_str)
            duration = int(duration_str)
        except ValueError:
            error = "Number of videos and duration must be integers."
            return render_template("index.html", error=error, message=message)

        if num_videos <= 10:
            error = "Number of videos must be greater than 10."
            return render_template("index.html", error=error, message=message)

        if duration <= 20:
            error = "Duration must be greater than 20 seconds."
            return render_template("index.html", error=error, message=message)

        if not is_valid_email(email):
            error = "Please enter a valid email address."
            return render_template("index.html", error=error, message=message)

        # Start background job
        reset_progress()

        def progress_cb(pct: int, msg: str):
            with progress_lock:
                progress_state["percent"] = pct
                progress_state["message"] = msg

        def job():
            try:
                output_dir = os.path.join(os.path.dirname(__file__), "output")
                os.makedirs(output_dir, exist_ok=True)
                audio_path = os.path.join(output_dir, "mashup.mp3")

                mashup_path = create_mashup(
                    singer, num_videos, duration, audio_path, progress_cb=progress_cb
                )

        # Zip the result
                zip_path = os.path.join(output_dir, "mashup.zip")
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(mashup_path, arcname=os.path.basename(mashup_path))

        # Send email with attachment INSIDE app context
                with app.app_context():
                    msg_obj = Message(
                        subject="Your Mashup File",
                        recipients=[email],
                    )
                    msg_obj.body = (
                        f"Hello,\n\nHere is your mashup for {singer} "
                        f"({num_videos} videos, {duration} seconds each).\n\nRegards."
                    )

                    with app.open_resource(zip_path) as fp:
                        msg_obj.attach("mashup.zip", "application/zip", fp.read())

                    mail.send(msg_obj)

                with progress_lock:
                    progress_state["done"] = True
                    if progress_state["percent"] < 100:
                        progress_state["percent"] = 100
                        progress_state["message"] = "Email sent."
            except Exception as e:
                print("JOB ERROR:", e)  # debug
                with progress_lock:
                    progress_state["error"] = f"Something went wrong while creating or sending mashup: {e}  "


        t = threading.Thread(target=job, daemon=True)
        t.start()

        return ("", 200)

    return render_template("index.html", error=error, message=message)


@app.route("/progress")
def get_progress():
    with progress_lock:
        print("PROGRESS:", progress_state)
        return jsonify(progress_state)


if __name__ == "__main__":
    app.run(debug=True)




