"""
render_contract: Utilities for rendering contract documents.

Includes functions for rendering DOCX templates, generating context from AFS data, and handling contract file operations.
"""

from docxtpl import DocxTemplate
from models.utils.lo_manager import ensure_lo_started, get_profile_dir, find_soffice
import os, subprocess, tempfile, time
from markupsafe import escape

def render_contract(template_path, out_docx, context):
    """Render a DOCX contract template with context data and save to output.

    Parameters
    ----------
    template_path : str
        Path to the DOCX template file.
    out_docx : str
        Path to save the rendered DOCX file.
    context : dict
        Context data for template rendering.

    Returns
    -------
    str
        Path to the saved DOCX file.
    """
    doc = DocxTemplate(template_path)
    doc.render(context) 
    doc.save(out_docx)
    return out_docx

def generate_context(afs_data: dict[str, str]):
    """Generate context dictionary for contract rendering from AFS data.

    Parameters
    ----------
    afs_data : dict[str, str]
        Data extracted from AFS application.

    Returns
    -------
    dict
        Context dictionary for template rendering.
    """
    context = {}
    for key, value in afs_data.items():
        placeholder = key.replace(' Number', '').replace(' ', '_').replace('-', '_').upper().strip()
        context.update({placeholder: "" if value is None else str(escape(value))})
    return context

def _abs(p):
    """Return the absolute path for a given path string.

    Parameters
    ----------
    p : str
        Path to convert to absolute.

    Returns
    -------
    str
        Absolute path.
    """
    return os.path.abspath(p)

def _wait_for(path, seconds=12):
    """Wait for a file to exist, polling periodically up to a timeout.

    Parameters
    ----------
    path : str
        Path to the file to wait for.
    seconds : int, optional
        Number of seconds to wait (default: 12).

    Returns
    -------
    bool
        True if the file exists within the timeout, False otherwise.
    """
    for _ in range(int(seconds*10)):
        if os.path.exists(path):
            return True
        time.sleep(0.1)
    return False

def _most_recent_pdf_in(dirpath, since_epoch):
    """Find the most recently modified PDF file in a directory since a given epoch time.

    Parameters
    ----------
    dirpath : str
        Directory to search for PDF files.
    since_epoch : float
        Only consider files modified after this epoch time.

    Returns
    -------
    str or None
        Path to the most recent PDF file, or None if none found.
    """
    latest = None; latest_mtime = since_epoch
    try:
        for name in os.listdir(dirpath):
            if name.lower().endswith(".pdf"):
                p = os.path.join(dirpath, name)
                try:
                    m = os.path.getmtime(p)
                    if m >= latest_mtime:
                        latest = p; latest_mtime = m
                except Exception:
                    pass
    except Exception:
        pass
    return latest

def convert_docx_to_pdf(docx_path, pdf_path=None, soffice_path=None, timeout=180):
    """Convert a DOCX file to PDF using LibreOffice in headless mode.

    Parameters
    ----------
    docx_path : str
        Path to the DOCX file to convert.
    pdf_path : str, optional
        Path to save the output PDF file (default: same as DOCX, with .pdf extension).
    soffice_path : str, optional
        Path to the soffice executable (default: auto-detect).
    timeout : int, optional
        Timeout in seconds for the conversion process (default: 180).

    Returns
    -------
    str
        Path to the saved PDF file.

    Raises
    ------
    FileNotFoundError
        If the DOCX file does not exist.
    RuntimeError
        If LibreOffice fails to produce a PDF.
    """
    docx_path = _abs(docx_path)
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"DOCX not found: {docx_path}")

    lo = ensure_lo_started()
    soffice = soffice_path or find_soffice()
    profile_dir = get_profile_dir()
    profile_uri = "file:///" + profile_dir.replace("\\", "/")

    #output location
    base_name = os.path.splitext(os.path.basename(docx_path))[0]
    if pdf_path is None:
        outdir = os.path.dirname(docx_path) or "."
        desired_pdf = os.path.join(outdir, base_name + ".pdf")
    else:
        desired_pdf = _abs(pdf_path)
        outdir = os.path.dirname(desired_pdf) or "."
    os.makedirs(outdir, exist_ok=True)

    expected_pdf = os.path.join(outdir, base_name + ".pdf")

    #command for converting docx to pdf
    cmd = [
        soffice,
        "--headless", 
        "--nologo", 
        "--nolockcheck", 
        "--norestore",
        "--nodefault", 
        "--nofirststartwizard",
        f"-env:UserInstallation={profile_uri}",
        "--convert-to", 
        "pdf:writer_pdf_Export",
        "--outdir", 
        outdir,
        docx_path,
    ]
    creationflags = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW

    # Run with cwd=outdir so LO has no excuse to drop files elsewhere
    started = time.time()
    res = subprocess.run(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True, 
        timeout=timeout, 
        creationflags=creationflags,
        cwd=outdir
    )

    # Wait for the exact expected name; if not, try to discover any new PDF
    if not _wait_for(expected_pdf, seconds=12):
        candidate = _most_recent_pdf_in(outdir, since_epoch=started - 1)
        if candidate and os.path.basename(candidate).lower().endswith(".pdf"):
            expected_pdf = candidate

    # Wait briefly for the output to appear
    if not _wait_for(expected_pdf, seconds=8):
        # last-ditch retry into a temp dir, then move
        with tempfile.TemporaryDirectory() as tmpout:
            cmd2 = cmd[:]
            cmd2[cmd2.index("--outdir")+1] = tmpout
            res2 = subprocess.run(
                cmd2, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                timeout=timeout, 
                creationflags=creationflags, 
                cwd=tmpout
            )
            tmp_pdf = os.path.join(tmpout, os.path.splitext(os.path.basename(docx_path))[0] + ".pdf")
            if os.path.exists(tmp_pdf):
                os.replace(tmp_pdf, desired_pdf)
                return desired_pdf

        raise RuntimeError(
            "LibreOffice did not produce a PDF.\n"
            f"CMD: {' '.join(cmd)}\nRETURN CODE: {res.returncode}\n"
            f"STDOUT:\n{res.stdout}\n\nSTDERR:\n{res.stderr}\n"
            f"Tried outdir: {outdir}\n"
            "If this persists, try converting to a temp directory"
            "and check Windows Defender 'Controlled Folder Access' rules for that folder."
        )

    # Rename to the desired name if needed
    if os.path.abspath(expected_pdf) != os.path.abspath(desired_pdf):
        os.replace(expected_pdf, desired_pdf)
    return desired_pdf