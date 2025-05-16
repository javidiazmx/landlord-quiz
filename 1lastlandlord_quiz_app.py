# ✅ Flask App (Updated for One-Question-at-a-Time Quiz)
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import csv
import re
import requests

app = Flask(__name__)
app.secret_key = 'secret_key_to_track_session'  # Required for session tracking

EMAILS_TO = ["new-deal9c8d81c829@newlead.leadsimple.com", "javier.diaz@gcrealtyinc.com"]
EMAIL_FROM = "javier.diaz@gcrealtyinc.com"
EMAIL_PASSWORD = "zcvj bnse ayqe lard"
GOOGLE_API_KEY = "AIzaSyCi_tyABZ6Yr0vzEbBXx80tq9qbcvEP-y0"

questions = [
    {"question": "How did you become a landlord?", "answers": [
        ("I couldn't sell and decided to rent", "Last Option Accidental"),
        ("Decided to rent instead of sell for now", "Try It Out Accidental"),
        ("Used to live there, now renting it", "Investor Converted Owner Occupant"),
        ("Bought intentionally as an investment", "First Time Investor"),
        ("Managed myself, but it's getting tiring", "Self Manager"),
        ("I'm unhappy with my current PM", "Not Happy with Current PM"),
        ("I’ve built a portfolio but want to outsource", "Self Manager with Portfolio"),
        ("I flip or wholesale and need short-term help", "Full Time Real Estate Investor")
    ]},
    {"question": "What matters most to you right now?", "answers": [
        ("Speed and no hassle", "Last Option Accidental"),
        ("Protecting investment & maximizing returns", "First Time Investor"),
        ("Having someone who understands my property", "Investor Converted Owner Occupant"),
        ("Freeing up my time", "Self Manager"),
        ("Better service than I have now", "Not Happy with Current PM")
    ]},
    {"question": "How involved do you want to be in property management?", "answers": [
        ("Hands-off", "Try It Out Accidental"),
        ("Informed but not day-to-day", "Self Manager with Portfolio"),
        ("Still want control", "Self Manager"),
        ("Hands-on but need help", "Not Happy with Current PM")
    ]},
    {"question": "What's your biggest concern right now?", "answers": [
        ("Finding a tenant quickly", "Last Option Accidental"),
        ("Maximizing cash flow", "First Time Investor"),
        ("Avoiding mistakes", "Try It Out Accidental"),
        ("Not doing everything myself", "Self Manager"),
        ("Getting advice and guidance", "Investor Converted Owner Occupant")
    ]}
]

suggestions = {
    "Last Option Accidental": "You need quick, no-hassle solutions. Look for a stress-free property manager.",
    "Try It Out Accidental": "You are testing this out — education and steady guidance will help.",
    "Investor Converted Owner Occupant": "You care about your property — find a manager who communicates well.",
    "First Time Investor": "You need expert help and local advice — a strong property manager is key.",
    "Self Manager": "You're ready to hand things off — but find someone who respects your experience.",
    "Not Happy with Current PM": "You want better service — make sure to find someone who listens.",
    "Self Manager with Portfolio": "You’re ready to scale — find a team you can trust and work closely with.",
    "Full Time Real Estate Investor": "You need fast, seamless service and a manager who understands investors."
}

def send_email(data):
    try:
        body = "\n".join([f"{k}: {v}" for k, v in data.items()])
        msg = MIMEText(body)
        msg["Subject"] = f"New Quiz Submission - {data.get('Name', 'No Name')}"
        msg["From"] = EMAIL_FROM
        msg["To"] = ", ".join(EMAILS_TO)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(msg["From"], EMAILS_TO, msg.as_string())
    except Exception as e:
        print("Email failed:", e)

@app.route('/', methods=['GET', 'POST'])
def quiz():
    if 'question_index' not in session:
        session['question_index'] = 0
        session['answers'] = []

    index = session['question_index']

    if request.method == 'POST':
        selected = request.form.get('answer')
        if selected:
    answers = session.get('answers', [])
    answers.append(selected)
    session['answers'] = answers
    session['question_index'] = session.get('question_index', 0) + 1
    index += 1

        if index >= len(questions):
            types = {key: 0 for key in suggestions}
            for a in session['answers']:
                types[a] += 1
            top_result = max(types, key=types.get)
            session.clear()
            return redirect(url_for('form', result=top_result))

    return render_template('quiz.html', question=questions[index], index=index, total=len(questions))

@app.route('/form', methods=['GET', 'POST'])
def form():
    result = request.args.get('result')
    if request.method == 'POST':
        info = {key: request.form.get(key, '') for key in [
            "Name", "Email", "Phone", "Property Address",
            "How Many Rental Units Do You own", "I Am", "Anything You Want To Share W/Us"]}

        if not all(info[field].strip() for field in ["Name", "Email", "Phone", "Property Address"]):
            return "Please fill in all required fields.", 400

        if not re.match(r"[^@]+@[^@]+\.[a-zA-Z]{2,}", info['Email']):
            return "Invalid email.", 400

        info["Quiz Result"] = result
        with open("quiz_results.csv", "a", newline='') as f:
            writer = csv.writer(f)
            if f.tell() == 0:
                writer.writerow(list(info.keys()))
            writer.writerow(list(info.values()))

        send_email(info)
        return render_template("result.html", result=result, message=suggestions[result])

    return render_template("form.html", result=result)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
