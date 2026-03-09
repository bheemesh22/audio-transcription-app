import os
import json
import datetime
from flask import Flask, render_template, redirect, url_for, request, session, flash, send_file, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import whisper
from deep_translator import GoogleTranslator
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet
from flask import Response

app = Flask(__name__)
app.config['SECRET_KEY'] = "supersecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['UPLOAD_FOLDER'] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db = SQLAlchemy(app)

# 🔥 LOAD WHISPER MODEL (use "base" or "tiny" if system is slow)
model = whisper.load_model("base")

# ---------------- DATABASE MODELS ---------------- #

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean, default=False)

class Transcript(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    title = db.Column(db.String(200))
    transcript = db.Column(db.Text)
    summary = db.Column(db.Text)
    translated_transcript = db.Column(db.Text)
    translated_summary = db.Column(db.Text)
    audio_file = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# ---------------- ADMIN ---------------- #

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin1234"

def is_logged_in():
    return "user_id" in session

def is_admin():
    return session.get("is_admin", False)

# ---------------- HELPER FUNCTIONS ---------------- #

def generate_title(text):
    words = text.split()
    if len(words) >= 6:
        return " ".join(words[:6]).title()
    return text.title()

def generate_summary(text):
    sentences = text.split(".")
    if len(sentences) >= 3:
        return ".".join(sentences[:3]) + "."
    return text

# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return redirect(url_for("login"))

# -------- REGISTER -------- #

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        if User.query.filter_by(username=username).first():
            flash("Username already exists")
            return redirect(url_for("register"))

        db.session.add(User(username=username, password=password))
        db.session.commit()
        flash("Registration successful")
        return redirect(url_for("login"))

    return render_template("register.html")

# -------- LOGIN -------- #

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["user_id"] = 0
            session["username"] = "admin"
            session["is_admin"] = True
            return redirect(url_for("dashboard"))

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            session["is_admin"] = False
            return redirect(url_for("dashboard"))

        flash("Invalid credentials")

    return render_template("login.html")

# -------- LOGOUT -------- #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# -------- DASHBOARD -------- #

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if not is_logged_in():
        return redirect(url_for("login"))

    if request.method == "POST":
        file = request.files.get("audio")

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            # 🔥 REAL TRANSCRIPTION
            result = model.transcribe(file_path)
            transcript_text = result["text"]

            # 🔥 TITLE + SUMMARY
            title = generate_title(transcript_text)
            summary_text = generate_summary(transcript_text)

            new_entry = Transcript(
                user_id=session["user_id"],
                title=title,
                transcript=transcript_text,
                summary=summary_text,
                audio_file=filename
            )

            db.session.add(new_entry)
            db.session.commit()
            flash("Transcription completed!")

    # ONLY LATEST TRANSCRIPT
    latest_transcript = Transcript.query.filter_by(
        user_id=session["user_id"]
    ).order_by(Transcript.created_at.desc()).first()

    return render_template("dashboard.html", transcript=latest_transcript)

# -------- TRANSLATE -------- #

@app.route("/translate/<int:id>", methods=["POST"])
def translate(id):
    entry = Transcript.query.get_or_404(id)
    language = request.form["language"]

    try:
        translated_text = GoogleTranslator(source='auto', target=language).translate(entry.transcript)
        translated_summary = GoogleTranslator(source='auto', target=language).translate(entry.summary)

        entry.translated_transcript = translated_text
        entry.translated_summary = translated_summary

        db.session.commit()
        flash("Translation completed successfully!")

    except Exception:
        flash("Translation failed. Use language codes like: hi, te, fr, de, es")

    return redirect(url_for("dashboard"))

# -------- DOWNLOAD -------- #




@app.route("/download/<int:id>/<string:type>")
def download(id, type):

    entry = Transcript.query.get_or_404(id)

    # -------- TEXT FILES --------

    if type == "transcript":
        content = entry.transcript
        filename = "transcript.txt"
        return Response(
            content,
            mimetype="text/plain",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )

    elif type == "summary":
        content = entry.summary
        filename = "summary.txt"
        return Response(
            content,
            mimetype="text/plain",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )
    
    elif type == "full_txt":
        content = f"""TITLE:
        {entry.title}
        
        TRANSCRIPT:
        {entry.transcript}
        
        SUMMARY:
        {entry.summary}
         """
        filename = "full_report.txt"
        return Response(
        content,
        mimetype="text/plain; charset=utf-8",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


    elif type == "translated_transcript":
        content = entry.translated_transcript or ""
        filename = "translated_transcript.txt"
        return Response(
            content,
            mimetype="text/plain",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )

    elif type == "translated_summary":
        content = entry.translated_summary or ""
        filename = "translated_summary.txt"
        return Response(
            content,
            mimetype="text/plain",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )

    # -------- JSON FILES --------

    elif type == "transcript_json":
        data = {"transcript": entry.transcript}
        filename = "transcript.json"

    elif type == "summary_json":
        data = {"summary": entry.summary}
        filename = "summary.json"

    elif type == "translated_transcript_json":
        data = {"translated_transcript": entry.translated_transcript}
        filename = "translated_transcript.json"

    elif type == "translated_summary_json":
        data = {"translated_summary": entry.translated_summary}
        filename = "translated_summary.json"

    elif type == "both_json":
        data = {
            "transcript": entry.transcript,
            "summary": entry.summary
        }
        filename = "transcript_summary.json"

    elif type == "translated_both_json":
        data = {
            "translated_transcript": entry.translated_transcript,
            "translated_summary": entry.translated_summary
        }
        filename = "translated_transcript_summary.json"

    else:
        return "Invalid download type"

    json_data = json.dumps(data, indent=4, ensure_ascii=False)

    return Response(
        json_data,
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )

    # -------- CREATE JSON --------




    # -------- CREATE TXT --------

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return send_file(file_path, as_attachment=True)

@app.route("/download_pdf/<int:id>")
def download_pdf(id):
    entry = Transcript.query.get_or_404(id)

    filename = f"transcript_{id}.pdf"
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    doc = SimpleDocTemplate(file_path)
    elements = []

    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    heading_style = styles["Heading1"]

    elements.append(Paragraph("Audio Transcript Report", heading_style))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(f"<b>Title:</b> {entry.title}", normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(f"<b>Transcript:</b>", normal_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(entry.transcript, normal_style))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(f"<b>Summary:</b>", normal_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(entry.summary, normal_style))

    doc.build(elements)

    return send_file(file_path, as_attachment=True)

# -------- SERVE UPLOADED FILES -------- #

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# -------- DELETE -------- #

@app.route("/delete/<int:id>")
def delete(id):
    entry = Transcript.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for("dashboard"))

# -------- HISTORY -------- #

@app.route("/history")
def history():
    if not is_logged_in():
        return redirect(url_for("login"))

    transcripts = Transcript.query.filter_by(
        user_id=session["user_id"]
    ).order_by(Transcript.created_at.desc()).all()

    return render_template("history.html", transcripts=transcripts)

# -------- ADMIN -------- #

@app.route("/admin")
def admin():
    if not is_admin():
        return redirect(url_for("dashboard"))

    users = User.query.all()
    transcripts = Transcript.query.all()

    return render_template("admin.html", users=users, transcripts=transcripts)


@app.route("/admin/delete_user/<int:user_id>")
def admin_delete_user(user_id):
    if not is_admin():
        return redirect(url_for("dashboard"))

    user = User.query.get_or_404(user_id)

    if user.username == "admin":
        flash("Cannot delete main admin")
        return redirect(url_for("admin"))

    # delete user's transcripts first
    Transcript.query.filter_by(user_id=user.id).delete()

    db.session.delete(user)
    db.session.commit()

    flash("User deleted successfully")
    return redirect(url_for("admin"))


@app.route("/admin/delete_transcript/<int:id>")
def admin_delete_transcript(id):
    if not is_admin():
        return redirect(url_for("dashboard"))

    entry = Transcript.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()

    flash("Transcript deleted successfully")
    return redirect(url_for("admin"))

# -------- RUN -------- #

if __name__ == "__main__":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    with app.app_context():
        db.create_all()

    app.run(debug=True)