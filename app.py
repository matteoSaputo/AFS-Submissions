# app.py
from flask import Flask, flash, request, render_template, redirect, session
from process_submission import prepare_submission, process_submission

import os

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

            afs_data, bus_name, matched_folder, match_score = prepare_submission(upload_path)
            
            session['upload_path'] = upload_path
            session['afs_data'] = afs_data
            session['bus_name'] = bus_name
            session['matched_folder'] = matched_folder

            if matched_folder and match_score >= 90:
                # Automatically use it
                return redirect("/confirm_folder_auto")
            else:
                # Ask user to confirm
                return render_template("confirm_folder.html", matched_folder=matched_folder, bus_name=bus_name)

    return render_template("index.html")


@app.route("/confirm_folder", methods=["POST"])
def confirm_folder():
    choice = request.form["choice"]
    if choice == "use_existing":
        customer_folder = os.path.join("G:/Shared drives/AFS Drive/Customer Info/Customer Info", session["matched_folder"])
    else:
        bus_name = session["bus_name"]
        customer_folder = os.path.join("G:/Shared drives/AFS Drive/Customer Info/Customer Info", bus_name)

    upload_path = session["upload_path"]
    afs_data = session["afs_data"]

    process_submission(upload_path, afs_data, session["bus_name"], customer_folder)
    
    flash(f"✅ Submission processed and saved successfully to {customer_folder}", "success")
    return redirect("/")

@app.route("/confirm_folder_auto")
def confirm_folder_auto():
    bus_name = session["bus_name"]
    customer_folder = os.path.join("G:/Shared drives/AFS Drive/Customer Info/Customer Info", session["matched_folder"])

    upload_path = session["upload_path"]
    afs_data = session["afs_data"]

    process_submission(upload_path, afs_data, bus_name, customer_folder)

    flash(f"✅ Submission processed and saved successfully to {customer_folder}", "success")
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, port=8000)
