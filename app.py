# app.py
from flask import Flask, request, render_template, redirect, url_for, session
from process_submission import prepare_submission, process_submission
import os
import uuid

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Needed for sessions!
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

@app.route("/confirm-folder", methods=["GET", "POST"])
def confirm_folder():
    afs_data = session.get('afs_data')
    bus_name = session.get('bus_name')
    suggested_folder = session.get('suggested_folder')

    if not (afs_data and bus_name):
        return redirect(url_for('index'))

    if request.method == "POST":
        decision = request.form.get("decision")
        if decision == "confirm":
            customer_folder = suggested_folder
        else:
            root = "G:/Shared drives/AFS Drive/Customer Info/Customer Info"
            customer_folder = os.path.join(root, bus_name)

        # Now fully process
        process_submission(session['upload_path'], afs_data, bus_name, customer_folder)

        # return render_template("success.html", customer_folder=customer_folder)

    return render_template("confirm_folder.html", suggested_folder=suggested_folder, bus_name=bus_name)

if __name__ == "__main__":
    app.run(debug=True, port=8000)
