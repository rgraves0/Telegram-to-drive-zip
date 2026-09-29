import os
import subprocess

DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "")

def extract_archive(archive_path: str, extract_dir: str, password: str = None) -> bool:
    pwd = password or DEFAULT_PASSWORD
    
    # 7z ဖြင့် ဖြည်ခြင်း
    cmd = ["7z", "x", archive_path, f"-o{extract_dir}", "-y"]
    if pwd:
        cmd.append(f"-p{pwd}")
    
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # 7z မရပါက unar ဖြင့် အရန်အနေနှင့် ဖြည်ခြင်း
    if result.returncode != 0:
        unar_cmd = ["unar", "-o", extract_dir, "-f", archive_path]
        if pwd:
            unar_cmd.extend(["-p", pwd])
        result = subprocess.run(unar_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        print(f"Extraction Error: {result.stderr}")
        return False
    return True

def compress_archive(source_path: str, output_path: str, fmt: str = "7z", password: str = None) -> bool:
    pwd = password or DEFAULT_PASSWORD
    
    # Folder ဖြစ်ပါက folder ထဲ ဝင်ပြီး အထဲက contents များကိုသာ zip ချုပ်မည်
    if os.path.isdir(source_path):
        cwd_dir = source_path
        target_items = ["."]
    else:
        cwd_dir = os.path.dirname(source_path)
        target_items = [os.path.basename(source_path)]

    if fmt == "rar":
        cmd = ["rar", "a", "-r", "-y"]
        if pwd:
            cmd.append(f"-p{pwd}")
        cmd.append(os.path.abspath(output_path))
        cmd.extend(target_items)
    else:
        cmd_fmt = "gzip" if fmt == "gz" else fmt
        cmd = ["7z", "a", f"-t{cmd_fmt}", os.path.abspath(output_path)]
        cmd.extend(target_items)
        cmd.extend(["-y", "-r"])
        
        if pwd and fmt in ["7z", "zip"]:
            cmd.append(f"-p{pwd}")
            if fmt == "7z":
                cmd.append("-mhe=on")

    result = subprocess.run(cmd, cwd=cwd_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Compression CLI Error: {result.stderr}")
        return False
    return True
