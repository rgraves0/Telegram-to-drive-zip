import os
import subprocess

DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "")

def extract_archive(file_path: str, extract_to: str, password: str = None) -> bool:
    """
    Zip, 7z, Rar, Tar, Gz စတာ အားလုံးကို extract လုပ်ပေးခြင်း
    """
    pwd = password or DEFAULT_PASSWORD
    # 7z x archive.ext -o/output/path -pPassword -y
    cmd = ["7z", "x", file_path, f"-o{extract_to}", "-y"]
    if pwd:
        cmd.append(f"-p{pwd}")
        
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

def compress_archive(source_path: str, output_archive_path: str, fmt: str = "7z", password: str = None) -> bool:
    """
    Default format 7z ဖြင့် compress လုပ်ခြင်း (zip, tar, gz လည်း ရနိုင်သည်)
    """
    pwd = password or DEFAULT_PASSWORD
    
    if fmt == "rar":
        # RAR အတွက် သီးသန့် rar command သုံးခြင်း
        cmd = ["rar", "a", "-r", "-y"]
        if pwd:
            cmd.append(f"-p{pwd}")
        cmd.extend([output_archive_path, source_path])
    else:
        # 7z, zip, tar, gz အတွက် 7z command သုံးခြင်း
        cmd = ["7z", "a", f"-t{fmt}", output_archive_path, source_path, "-y"]
        if pwd and fmt in ["7z", "zip"]:
            cmd.append(f"-p{pwd}")
            if fmt == "7z":
                # 7z format မှာ ဖိုင်နာမည်တွေကိုပါ encrypt လုပ်ရန် (-mhe=on)
                cmd.append("-mhe=on")

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0
