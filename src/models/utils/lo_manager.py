"""
lo_manager: Utility for managing LibreOffice integration and locating soffice executables.

Provides functions to find soffice, manage candidate paths, and handle LibreOffice startup and shutdown.
"""

import atexit
import os
import shutil
import subprocess
import sys
import tempfile
import time

def _abs(p): return os.path.abspath(p)

def _candidate_paths(base_dir):
    if not base_dir:
        return []
    return [
        os.path.join(base_dir, "integrations", "libreoffice", "program", "soffice.com"),
        os.path.join(base_dir, "integrations", "libreoffice", "program", "soffice.exe"),
        os.path.join(base_dir, "LibreOffice", "program", "soffice.com"),
        os.path.join(base_dir, "LibreOffice", "program", "soffice.exe"),
        os.path.join(base_dir, "libreoffice", "program", "soffice.com"),
        os.path.join(base_dir, "libreoffice", "program", "soffice.exe"),
    ]

def find_soffice(explicit_path: str | None = None) -> str:
    """Find the path to the LibreOffice soffice executable.

    Parameters
    ----------
    explicit_path : str or None, optional
        Explicit path to soffice (default: None).

    Returns
    -------
    str
        Path to the soffice executable.
    """
    # 0) explicit and env
    cands = []
    if explicit_path:
        cands.append(_abs(explicit_path))
    envp = os.environ.get("AFS_SOFFICE_PATH")
    if envp:
        cands.append(_abs(envp))

    # 1) EXE dir (works for one-file & one-dir)
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else None
    cands += _candidate_paths(exe_dir)

    # 2) _MEIPASS (one-file extraction dir)
    meipass = getattr(sys, "_MEIPASS", None)
    cands += _candidate_paths(meipass)

    # 3) current working dir (just in case)
    cands += _candidate_paths(os.getcwd())

    # 4) typical installs & PATH
    cands += [
        r"C:\Program Files\LibreOffice\program\soffice.com",
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.com",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        shutil.which("soffice"),
    ]

    # dedupe while preserving order
    seen, ordered = set(), []
    for p in cands:
        if p and p not in seen and os.path.exists(p):
            seen.add(p); ordered.append(_abs(p))

    if not ordered:
        raise FileNotFoundError("LibreOffice (soffice) not found. "
                                "Place 'integrations\\libreoffice\\program\\soffice.com' next to the EXE, "
                                "or set AFS_SOFFICE_PATH to soffice(.com).")
    return ordered[0]

def get_profile_dir():
    """ A stable profile path for LibreOffice (create on first run, reuse on subsequent)"""
    tempdir = os.getenv("LOCALAPPDATA", tempfile.gettempdir())
    base = os.path.join(tempdir, "LO_Profile")
    os.makedirs(base, exist_ok=True)
    return base

class LibreOfficeManager:
    """Manager for starting and stopping a LibreOffice instance."""

    def __init__(self):
        """Initialize the LibreOfficeManager, locating soffice and profile directory."""
        self.soffice = find_soffice()
        self.profile = get_profile_dir()
        self.proc: subprocess.Popen = None

    def start(self):
        """Start LibreOffice in headless mode."""
        if self.proc and self.proc.poll() is None:
            return # already running
        profile_uri = "file:///" + self.profile.replace("\\", "/")
        # create command for starting headless LibreOffice
        cmd = [
            self.soffice,
            "--headless", 
            "--nologo", 
            "--nodefault", 
            "--nofirststartwizard",
            f"-env:UserInstallation={profile_uri}",
            '--accept=socket,host=127.0.0.1,port=2002;urp'
        ]
        flags = 0x08000000 if os.name == 'nt' else 0 #hide console
        self.proc = subprocess.Popen( # create child process
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags
        )
        time.sleep(0.8)

    def stop(self):
        """Stop the running instance of LibreOffice, if any."""
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.terminate()
                self.proc.wait(timeout=3)
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass
        self.proc = None

_lo_mgr: LibreOfficeManager = None
def ensure_lo_started():
    """Ensure that a LibreOffice instance is running; start it if not."""
    global _lo_mgr
    if _lo_mgr is None:
        _lo_mgr = LibreOfficeManager()
        _lo_mgr.start()
        atexit.register(_lo_mgr.stop)
    else:
        _lo_mgr.start()
    return _lo_mgr