from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory storage
applications = []

# Email Config
EMAIL_ADDRESS = "carrerbridge2@gmail.com"
EMAIL_PASSWORD = "jaur likk hyha xzru"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Minimum required years of experience per job title
MINIMUM_YOE_REQUIREMENTS = {
    "Software Developer": 2,
    "Data Analyst": 1,
    "Network Administrator": 3,
    "Junior Engineeer": 0,
    "ETL Developer": 2
}

# Email helpers
def send_email(receiver_email, subject, body):
    if not receiver_email:
        return
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, receiver_email, msg.as_string())
        server.quit()
        print(f"✅ Email sent to {receiver_email}")
    except Exception as e:
        print(f"❌ Email error: {e}")

def send_acceptance_email(email, name, job, company):
    subject = "🎉 Application Accepted - CareerBridge"
    body = f"""
    Dear {name},

    Congratulations! Your application for the position of {job} at {company} has been accepted based on your experience.

    Our team will reach out to you shortly for the next steps.

    Best regards,  
    CareerBridge Team
    """
    send_email(email, subject, body)

def send_rejection_email(email, name, job, company):
    subject = "⚠ Application Status - CareerBridge"
    body = f"""
    Dear {name},

    Thank you for applying for the position of {job} at {company}.

    Unfortunately, your application was not accepted due to insufficient experience for this role.

    Keep applying, and we wish you success in your job search.

    Best regards,  
    CareerBridge Team
    """
    send_email(email, subject, body)

@app.route('/submit', methods=['POST'])
def submit_application():
    try:
        data = request.json
        data['timestamp'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        applications.append(data)

        name = data['name']
        email = data['email']
        job_title = data['jobTitle']
        company = data['company']
        yoe = int(data.get('yoe', 0))  # Years of experience

        min_yoe_required = MINIMUM_YOE_REQUIREMENTS.get(job_title, 0)

        if yoe >= min_yoe_required:
            send_acceptance_email(email, name, job_title, company)
        else:
            send_rejection_email(email, name, job_title, company)

        socketio.emit('new_application', data)
        return jsonify({"message": "Application received"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@app.route('/applications', methods=['GET'])
def get_applications():
    return jsonify(applications), 200
if __name__ == "__main__":
    socketio.run(app, debug=True)
