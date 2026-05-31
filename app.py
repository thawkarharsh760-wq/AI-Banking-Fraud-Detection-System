from flask import Flask, render_template, request, redirect, url_for
import joblib
import sqlite3
from flask import send_file
from reportlab.pdfgen import canvas

app = Flask(__name__)

model = joblib.load("fraud_model.pkl")
blacklist_accounts = [

    "Fraudster123",
    "Scammer001",
    "FakeAccount",
    "BlacklistedUser"

]

# Transaction History List
history = []

# SQLite Database Connection
conn = sqlite3.connect('transactions.db', check_same_thread=False)

cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    receiver TEXT,
    amount REAL,
    city TEXT,
    time TEXT,
    score INTEGER,
    status TEXT

)
''')

conn.commit()

# ================= LOGIN PAGE =================

@app.route('/login', methods=['GET', 'POST'])

def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin123":

            return redirect(url_for('home'))

    return render_template('login.html')
   # ================= PDF REPORT =================

@app.route('/download_report')
def download_report():

    pdf = canvas.Canvas("Fraud_Report.pdf")

    pdf.setTitle("AI Fraud Detection Report")

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(180, 800, "AI Fraud Detection Report")

    y = 760

    for item in history:

        pdf.setFont("Helvetica", 10)

        pdf.drawString(
            20,
            y,
            f"Sender: {item['sender']} | Receiver: {item['receiver']} | Amount: Rs.{item['amount']} | Risk: {item['score']}% | Status: {item['status']}"
        )

        y -= 20

        if y < 50:
            pdf.showPage()
            y = 800

    pdf.save()

    return send_file(
        "Fraud_Report.pdf",
        as_attachment=True
    )

# ================= MAIN PAGE =================

@app.route('/')

def main():

    return redirect(url_for('login'))

# ================= DASHBOARD =================

@app.route('/dashboard', methods=['GET', 'POST'])

def home():

    result = ""
    recommendation = ""
    sms_alert = ""
    email_alert = ""
    blacklist_alert = ""
    
    score = 0
    trust = 100

    if request.method == 'POST':

        sender = request.form['sender']
        receiver = request.form['receiver']
        if receiver in blacklist_accounts:

         score += 50

        blacklist_alert = "🚫 Known Fraudulent Account Detected"
        amount = float(request.form['amount'])
        otp = request.form['otp']
        transaction_time = request.form['time']
        city = request.form['city']

        hour = int(transaction_time.split(':')[0])

        # Amount Risk
        if amount > 100000:
            score += 60

        elif amount > 50000:
            score += 30

        # OTP Risk
        if otp == "no":
            score += 40

        # Night Transaction Risk
        if hour >= 23 or hour <= 5:
            score += 25

        # Unknown Location Risk
        if city == "Unknown":
            score += 35

        # Trust Score
        trust = max(0, 100 - score)

        # Final Result
        if score >= 70:

            result = "🔴 High Risk Fraud Transaction"

            recommendation = "🚨 Freeze Account & Contact Bank Immediately"
            
            sms_alert = "📱 SMS Alert Sent To Customer"
            
            email_alert = "📧 Email Alert Sent To Security Team"
            if blacklist_alert:

             recommendation = "🚨 Blacklisted Receiver Found - Transaction Blocked"

        elif score >= 30:

            result = "🟡 Medium Risk Transaction"

            recommendation = "⚠ Verify User Identity & Transaction Details"

        else:

            result = "🟢 Safe Transaction"

            recommendation = "✅ Transaction Approved"

        # Save Transaction History
        history.append({

            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "city": city,
            "time": transaction_time,
            "score": score,
            "status": result

        })

        # Save to SQLite Database
        cursor.execute('''
        INSERT INTO transactions
        (sender, receiver, amount, city, time, score, status)

        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (

            sender,
            receiver,
            amount,
            city,
            transaction_time,
            score,
            result

        ))

        conn.commit()

    # Dashboard Analytics

    total_transactions = len(history)

    fraud_count = 0
    safe_count = 0

    for item in history:

        if "High Risk" in item['status']:

            fraud_count += 1

        else:

            safe_count += 1

    return render_template(

        'index.html',

        result=result,
        score=score,
        trust=trust,
        recommendation=recommendation,
        
        sms_alert=sms_alert,
        email_alert=email_alert,
        blacklist_alert=blacklist_alert,

        history=history,

        total_transactions=total_transactions,
        fraud_count=fraud_count,
        safe_count=safe_count

    )
    @app.route('/clear_history')
    def clear_history():

     history.clear()

    cursor.execute("DELETE FROM transactions")

    conn.commit()

    return redirect(url_for('home'))
    @app.route('/logout')
    def logout():
     return redirect(url_for('login'))

if __name__ == "__main__":

    app.run(debug=True)