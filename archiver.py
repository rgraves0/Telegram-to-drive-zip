import os
import subprocess

DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "")

def extract_archive(archive_path: str, extract_dir: str, password: str = None) -> bool:
    pwd = password or DEFAULT_PASSWORD
    cmd = ["7z", "x", archive_path, f"-o{extract_dir}", "-y"]
    if pwd:
        cmd.append(f"-p{pwd}")
    
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

def compress_archive(source_path: str, output_path: str, fmt: str = "7z", password: str = None) -> bool:
    pwd = password or DEFAULT_PASSWORD
    
    if fmt == "rar":
        cmd = ["rar", "a", "-r", "-y"]
        if pwd:
            cmd.append(f"-p{pwd}")
        cmd.extend([output_path, source_path])
    else:
        cmd = ["7z", "a", f"-t{fmt}", output_path, source_path, "-y"]
        if pwd and fmt in ["7z", "zip"]:
            cmd.append(f"-p{pwd}")
            if fmt == "7z":
                cmd.append("-mhe=on")  # Filename များကိုပါ ဝှက်ရန်

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0
