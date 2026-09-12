import json
import os
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

import dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

dotenv.load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
DATA_DIR = BASE_DIR / "data"
MESSAGES_FILE = DATA_DIR / "messages.json"
PROJECTS_FILE = DATA_DIR / "projects.json"

app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR / "static"),
    static_url_path="/static",
    template_folder=str(FRONTEND_DIR / "templates"),
)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-in-production")


def load_projects():
    """Load project data from JSON instead of a database."""
    try:
        projects = json.loads(PROJECTS_FILE.read_text(encoding="utf-8"))
        return projects if isinstance(projects, list) else []
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


def get_project(project_id):
    return next((p for p in load_projects() if p.get("id") == project_id), None)


def save_message(name: str, email: str, message: str) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    messages = []

    if MESSAGES_FILE.exists():
        try:
            messages = json.loads(MESSAGES_FILE.read_text(encoding="utf-8"))
            if not isinstance(messages, list):
                messages = []
        except (json.JSONDecodeError, OSError):
            messages = []

    messages.append({
        "name": name,
        "email": email,
        "message": message,
        "received_at": datetime.now(timezone.utc).isoformat(),
    })
    MESSAGES_FILE.write_text(
        json.dumps(messages, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def send_contact_email(name: str, sender_email: str, message: str) -> None:
    """Send a notification to the portfolio owner using SMTP settings from env vars."""
    smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_username = os.environ.get("SMTP_USERNAME")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    recipient = os.environ.get("CONTACT_EMAIL") or smtp_username

    if not smtp_username or not smtp_password or not recipient:
        raise RuntimeError("Email settings are not configured.")

    email = EmailMessage()
    email["Subject"] = f"New portfolio message from {name}"
    email["From"] = smtp_username
    email["To"] = recipient
    email["Reply-To"] = sender_email
    email.set_content(f"""You received a new message through your portfolio.\n\n
Name: {name}\n
Email: {sender_email}\n\n
Message:\n{message}\n\n
Received: {datetime.now(timezone.utc).isoformat()}\n""")

    with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as smtp:
        smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.send_message(email)


@app.route("/")
def home():
    return render_template("index.html", projects=load_projects())


@app.route("/projects")
def projects():
    return render_template("projects.html", projects=load_projects())


@app.route("/projects/<project_id>")
def project_detail(project_id):
    project = get_project(project_id)
    if project is None:
        return render_template("404.html"), 404
    return render_template("project_detail.html", project=project)


@app.post("/contact")
def contact():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    message = request.form.get("message", "").strip()

    if not name or not email or not message:
        flash("Please fill in your name, email and message.", "error")
        return redirect(url_for("home") + "#contact")

    if "@" not in email or len(email) > 254:
        flash("Please enter a valid email address.", "error")
        return redirect(url_for("home") + "#contact")

    save_message(name, email, message)

    try:
        send_contact_email(name, email, message)
        flash("Thanks! Your message was sent successfully.", "success")
    # except (OSError, smtplib.SMTPException, ValueError, RuntimeError) as exc:
    #     app.logger.warning("Contact email could not be sent: %s", exc)
    #     flash("Your message was saved, but email notification could not be sent.", "error")
    except Exception as exc:
        app.logger.exception("Contact email failed")
        flash(f"Email error: {type(exc).__name__}: {exc}", "error")

    return redirect(url_for("home") + "#contact")


@app.errorhandler(413)
def request_too_large(_error):
    flash("The submitted data is too large.", "error")
    return redirect(url_for("home") + "#contact")


if __name__ == "__main__":
    app.run(debug=True)
