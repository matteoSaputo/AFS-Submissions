from docxtpl import DocxTemplate
import os, sys, subprocess, shutil, tempfile, time

def render_contract(template_path, out_docx, context):
    doc = DocxTemplate(template_path)
    doc.render(context) 
    doc.save(out_docx)
    return out_docx

def generate_context(afs_data: dict[str, str]):
    context = {}
    for key, value in afs_data.items():
        placeholder = key.replace(' Number', '').replace(' ', '_').upper().strip()
        context.update({placeholder: value})
    return context

def _abs(p): return os.path.abspath(p)

def _resource_dir():
    if hasattr(sys, "_MEIPASS"):  # PyInstaller one-file temp
        return sys._MEIPASS
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.getcwd()

def _check_lo_layout(soffice_path: str):
    prog = os.path.dirname(soffice_path)
    root = os.path.dirname(prog)
    must = [
        os.path.join(prog, "fundamental.ini"),
        os.path.join(root, "share"),
        os.path.join(root, "URE"),
    ]
    return [p for p in must if not os.path.exists(p)]

def find_soffice(explicit=None):
    cands = []
    if explicit:
        explicit = _abs(explicit)
        base_prog = os.path.dirname(explicit)
        for name in ("soffice.com", "soffice.exe"):
            p = os.path.join(base_prog, name)
            if os.path.exists(p): cands.append(p)
    envp = os.environ.get("AFS_SOFFICE_PATH")
    if envp:
        envp = _abs(envp)
        base_prog = os.path.dirname(envp)
        for name in ("soffice.com", "soffice.exe"):
            p = os.path.join(base_prog, name)
            if os.path.exists(p): cands.append(p)

    base = _resource_dir()
    for rel in [
        ("integrations","libreoffice","program","soffice.com"),
        ("integrations","libreoffice","program","soffice.exe"),
        ("integrations","LibreOffice","program","soffice.com"),
        ("integrations","LibreOffice","program","soffice.exe"),
        ("LibreOffice","program","soffice.com"),
        ("LibreOffice","program","soffice.exe"),
        ("libreoffice","program","soffice.com"),
        ("libreoffice","program","soffice.exe"),
        (r"C:\Program Files\LibreOffice\program","soffice.com"),
        (r"C:\Program Files\LibreOffice\program","soffice.exe"),
        (r"C:\Program Files (x86)\LibreOffice\program","soffice.com"),
        (r"C:\Program Files (x86)\LibreOffice\program","soffice.exe"),
    ]:
        p = os.path.join(base, *rel) if isinstance(rel, tuple) else rel
        if os.path.exists(p): cands.append(_abs(p))

    seen, ordered = set(), []
    for p in cands:
        if p and p not in seen:
            seen.add(p); ordered.append(p)

    for p in ordered:
        if not _check_lo_layout(p):
            return p
    if ordered:
        missing = _check_lo_layout(ordered[0])
        raise FileNotFoundError("LibreOffice bundle looks incomplete. Missing: "
                                + ", ".join(missing) + f"\nCandidate: {ordered[0]}")
    raise FileNotFoundError("LibreOffice (soffice) not found.")

def _wait_for(path, seconds=12):
    for _ in range(int(seconds*10)):
        if os.path.exists(path):
            return True
        time.sleep(0.1)
    return False

def _most_recent_pdf_in(dirpath, since_epoch):
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
    docx_path = _abs(docx_path)
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"DOCX not found: {docx_path}")

    soffice = find_soffice(soffice_path)

    if pdf_path is None:
        outdir = os.path.dirname(docx_path) or "."
        desired_pdf = os.path.join(outdir, os.path.splitext(os.path.basename(docx_path))[0] + ".pdf")
    else:
        desired_pdf = _abs(pdf_path)
        outdir = os.path.dirname(desired_pdf) or "."
    os.makedirs(outdir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(docx_path))[0]
    expected_pdf = os.path.join(outdir, base_name + ".pdf")

    # Private profile to avoid first-run dialogs
    prof = tempfile.mkdtemp(prefix="lo_profile_")
    prof_uri = "file:///" + prof.replace("\\", "/")

    cmd = [
        soffice,
        "--headless", "--nologo", "--nolockcheck", "--norestore",
        "--nodefault", "--nofirststartwizard",
        f"-env:UserInstallation={prof_uri}",
        "--convert-to", "pdf:writer_pdf_Export",
        "--outdir", outdir,
        docx_path,
    ]
    creationflags = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW

    # Run with cwd=outdir so LO has no excuse to drop files elsewhere
    started = time.time()
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, timeout=timeout, creationflags=creationflags,
                         cwd=outdir)

    # Wait for the exact expected name; if not, try to discover any new PDF
    if not _wait_for(expected_pdf, seconds=12):
        candidate = _most_recent_pdf_in(outdir, since_epoch=started - 1)
        if candidate and os.path.basename(candidate).lower().endswith(".pdf"):
            expected_pdf = candidate

    try:
        shutil.rmtree(prof, ignore_errors=True)
    except Exception:
        pass

    if not os.path.exists(expected_pdf):
        # Last-ditch retry: write into a temp dir, then move
        with tempfile.TemporaryDirectory() as tmpout:
            cmd2 = cmd[:]
            cmd2[ cmd2.index("--outdir") + 1 ] = tmpout
            res2 = subprocess.run(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  text=True, timeout=timeout, creationflags=creationflags,
                                  cwd=tmpout)
            tmp_expected = os.path.join(tmpout, base_name + ".pdf")
            if _wait_for(tmp_expected, seconds=12):
                os.replace(tmp_expected, desired_pdf)
                return desired_pdf

        raise RuntimeError(
            "LibreOffice did not produce a PDF.\n"
            f"CMD: {' '.join(cmd)}\nRETURN CODE: {res.returncode}\n"
            f"STDOUT:\n{res.stdout}\n\nSTDERR:\n{res.stderr}\n"
            f"Tried outdir: {outdir}\n"
            "If this persists, try converting to a temp directory (we do this automatically above) "
            "and check Windows Defender 'Controlled Folder Access' rules for that folder."
        )

    # Rename to the desired name if needed
    if os.path.abspath(expected_pdf) != os.path.abspath(desired_pdf):
        os.replace(expected_pdf, desired_pdf)
    return desired_pdf