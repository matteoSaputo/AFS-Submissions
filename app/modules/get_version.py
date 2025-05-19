import os
from modules.resource_path import resource_path

def get_version():
    version_file = resource_path("info/version.txt")
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            return f.read().strip()
    return "vUnknown"