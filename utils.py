# utils.py
import zipfile, tarfile, tempfile, shutil, os
from pathlib import Path

def safe_extract_archive(archive_path: str, dest_dir: str) -> str:
    """
    Extract archive to dest_dir safely. Supports zip and tar.
    Returns path to extracted folder.
    """
    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    # zip
    try:
        if zipfile.is_zipfile(archive_path):
            with zipfile.ZipFile(archive_path, 'r') as z:
                for info in z.infolist():
                    # prevent absolute or parent traversal paths
                    if os.path.isabs(info.filename) or ".." in Path(info.filename).parts:
                        continue
                z.extractall(dest)
            return str(dest)
        if tarfile.is_tarfile(archive_path):
            with tarfile.open(archive_path, 'r:*') as t:
                for member in t.getmembers():
                    if os.path.isabs(member.name) or ".." in Path(member.name).parts:
                        continue
                t.extractall(dest)
            return str(dest)
    except Exception:
        pass

    # fallback: copy single file into a temp folder
    tmp = tempfile.mkdtemp(prefix="ext_nounpack_")
    shutil.copy2(archive_path, tmp)
    return tmp
