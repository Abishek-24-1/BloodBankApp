from flask import Flask, jsonify, render_template, request
import mysql.connector
from datetime import date

app = Flask(__name__)

# ---------------- MYSQL CONNECTION ----------------
db = mysql.connector.connect(
    host="localhost",
    user="bloodapp",
    password="1234",
    database="BloodBank"
)
# ---------------- HOME PAGE ----------------
@app.route('/')
def home():
    return render_template('index.html')
# ---------------- SEARCH DONOR ----------------
@app.route('/donor/<idcard>')
def donor(idcard):

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM Donor WHERE IDCardNumber=%s
    """, (idcard,))

    donor = cursor.fetchone()

    if not donor:
        return jsonify({"message": "Donor not found"})

    # ---------------- ELIGIBILITY CALCULATION ----------------
    last_date = donor["LastDonationDate"]

    if isinstance(last_date, str):
        last_date = date.fromisoformat(last_date)

    days_diff = (date.today() - last_date).days

    if days_diff >= 90 and donor["InfectionStatus"] == "Negative":
        eligible = "Yes"
    else:
        eligible = "No"

    # ---------------- FINAL RESPONSE ----------------
    return jsonify({
        "Name": donor["Name"],
        "Address": donor["Address"],
        "AadhaarCardNumber": donor["IDCardNumber"],
        "Phone": donor["Phone"],
        "BloodGroup": donor["BloodGroup"],
        "TTIStatus": donor["InfectionStatus"],
        "LastDonationDate": str(donor["LastDonationDate"]),
        "Eligible": eligible,
        "AadhaarImage": donor["AadhaarImage"]
    })


# ---------------- ADD DONOR ----------------
@app.route('/add_donor', methods=['GET', 'POST'])
def add_donor():

    # SHOW FORM
    if request.method == 'GET':
        return render_template('add_donor.html')

    # INSERT INTO DATABASE
    data = request.form
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO Donor
        (Name, Address, IDCardNumber, Phone, BloodGroup, LastDonationDate, InfectionStatus, AadhaarImage)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        data['Name'],
        data['Address'],
        data['IDCardNumber'],
        data['Phone'],
        data['BloodGroup'],
        data['LastDonationDate'],
        data['InfectionStatus'],
        data['AadhaarImage']
    ))

    db.commit()

    return jsonify({
        "message": "Donor added successfully",
        "IDCardNumber": data['IDCardNumber']
    })


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
