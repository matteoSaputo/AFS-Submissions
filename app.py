from flask import Flask, request, render_template, redirect, url_for
from process_submission import process_submission, prepare_submission
import os

app = Flask(__name__)
UPLOAD_FOLDER = './data/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("pdf")
        if file:
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], "document.pdf")
            file.save(upload_path)

            try:
                afs_data, bus_name, suggested_folder = prepare_submission(upload_path)
                return render_template("index.html", 
                                       afs_data=afs_data,
                                       bus_name=bus_name,
                                       suggested_folder=suggested_folder)
            except Exception as e:
                return f"Error: {str(e)}"

    return render_template("index.html")

@app.route("/confirm", methods=["POST"])
def confirm():
    use_suggested = request.form.get("use_suggested") == "yes"
    afs_data = request.form.get("afs_data")  # Replace with proper session/state handling
    bus_name = request.form.get("bus_name")  # Replace with proper session/state handling
    folder_path = request.form.get("suggested_folder") if use_suggested else None

    try:
        final_path = process_submission("./data/uploads/document.pdf")
        return f"Submission successfully processed and saved to:<br>{final_path}"
    except Exception as e:
        return f"Error during submission: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True, port=8000)