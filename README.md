﻿# AFS-Submissions-Tool

**Latest Version:** 1.2 [Download here](https://github.com/matteoSaputo/AFS-Submissions/releases/download/v1.2/AFS_Submission_Tool_v1.2.exe)  
**Author:** Matteo Saputo  
**Company:** Alternative Funding Solutions (AFS)  
**License:** MIT  
**Repository:** [AFS-Submissions](https://github.com/matteoSaputo/AFS-Submissions/)

---

## 📌 Overview

AFS Submissions Tool is an internal Python application designed for Alternate Funding Solutions (AFS) to streamline the processing of business applications for Merchant Cash Advance (MCA) brokerage operations.  
The tool automates the extraction of key data from PDF applications, organizes submissions into a shared Drive of the user's choice, and generates packages for third-party lenders.  
A modern Tkinter-based interface ensures the team can work quickly and efficiently.

---

## 🧰 Features

- **Drag-and-Drop Interface:** Easily upload application files via a simple drag-and-drop mechanism.
- **PDF Analysis:** Uses PyMuPDF and pdfplumber to extract relevant data from application PDFs.
- **Automated Folder Matching:** Suggests appropriate folders in the shared Google Drive based on application content.
- **Submission Packaging:** Prepares and organizes submission packages for third-party lenders.

---

## 🗂️ Project Structure

```
AFS-Submissions/
├── assets/                   # Static assets (e.g., spinner.gif)
├── data/
│   └── uploads/              # Directory for uploaded files
├── info/                     # Informational files
├── src/
│   ├── controllers/          # Controller modules
│   ├── models/               # Business logic and data processing
│   └── views/                # GUI components
├── AFS-Submissions-Tool.spec # PyInstaller spec file
├── build_and_deploy.bat      # Windows batch script for building and deploying
└── README.md                 # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

### Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/matteoSaputo/AFS-Submissions.git
   cd AFS-Submissions
   ```

2. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   # On Mac/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r info/requirements.txt
   ```

4. **Run the Application:**
   ```bash
   python src/main.py
   ```

---

## 🖥️ Usage

1. **Launch the Application:** Run the main script to open the GUI.
2. **Select Drive Folder:** On first launch, you'll be prompted to select your shared Google Drive folder.
3. **Upload Files:** Drag and drop application PDFs or use the "Select Files" button.
4. **Process Applications:** The tool will analyze the PDFs and suggest appropriate folders.
5. **Confirm or Create Folder:** Use the suggested folder or create a new one.
6. **Finalize Submission:** The tool organizes the files and prepares the submission package.

---

## 🛠️ Development

### Building Executable (Windows)

To create a standalone executable using PyInstaller:

```bash
pyinstaller AFS-Submissions-Tool.spec
```

This will generate a `dist/` directory containing the executable.

---

## 🚧 Roadmap

Planned features for future versions:

- **📄 Contract Automation:**  
  Add a dedicated page for generating line-of-credit contracts based on parsed data, with support for standard templates and dynamic field insertion.

- **📧 Email Integration:**  
  Build in functionality for writing and sending emails directly from the tool, using pre-defined templates to submit completed packages to lenders.

- **🧪 Test Mode:**  
  Add a sandbox/test mode to simulate submissions and email dispatch without affecting live systems.

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.    

---

## 🤝 Contributing

*Contribution guidelines to be added in future versions.*
