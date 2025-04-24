# app.py
from flask import Flask, request, render_template, redirect, send_from_directory
from process_submission import process_submission
import os

app = Flask(__name__)
UPLOAD_FOLDER = './data/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["pdf"]
        if file:
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], "document.pdf")
            file.save(upload_path)

            try:
                customer_folder = process_submission(upload_path)
                # return f"Submission processed and saved to:<br>{customer_folder}"
            except Exception as e:
                return f"Error: {str(e)}"

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=8000)
