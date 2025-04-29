# app.py
from flask import Flask, request, render_template, redirect, url_for, session
from process_submission import prepare_submission, process_submission
import os
import uuid

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Needed for sessions
UPLOAD_FOLDER = './data/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["pdf"]
        if file:
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], "document.pdf")
            file.save(upload_path)

            afs_data, bus_name, suggested_folder = prepare_submission(upload_path)

            # Save data in session
            session['afs_data'] = afs_data
            session['bus_name'] = bus_name
            session['upload_path'] = upload_path
            session['suggested_folder'] = suggested_folder

            return redirect(url_for('confirm_folder'))

    return render_template("index.html")

@app.route("/confirm_folder", methods=["POST"])
def confirm_folder():
    choice = request.form["choice"]
    if choice == "use_existing":
        customer_folder = session["matched_folder"]
    else:
        # User clicked "Create new folder"
        bus_name = session["bus_name"]
        root = "G:/Shared drives/AFS Drive/Customer Info/Customer Info"
        customer_folder = os.path.join(root, bus_name)

    upload_path = session["upload_path"]
    afs_data = session["afs_data"]

    process_submission(upload_path, afs_data, session["bus_name"], customer_folder)

    return f"✅ Submission processed and saved to:<br>{customer_folder}"

if __name__ == "__main__":
    app.run(debug=True, port=8000)
