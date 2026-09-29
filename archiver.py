import os
import subprocess

DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "")

def extract_archive(archive_path: str, extract_dir: str, password: str = None):
    pwd = password or DEFAULT_PASSWORD
    
    cmd = ["7z", "x", archive_path, f"-o{extract_dir}", "-y"]
    if pwd:
        cmd.append(f"-p{pwd}")
    
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        unar_cmd = ["unar", "-o", extract_dir, "-f", archive_path]
        if pwd:
            unar_cmd.extend(["-p", pwd])
        result = subprocess.run(unar_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        err = result.stderr or result.stdout
        return False, err
    return True, ""

def compress_archive(source_path: str, output_path: str, fmt: str = "7z", password: str = None):
    pwd = password or DEFAULT_PASSWORD
    
    # Path အမှန်တကယ် ရှိမရှိ စစ်ဆေးခြင်း
    if not os.path.exists(source_path):
        return False, f"Source path not found: {source_path}"

    abs_output = os.path.abspath(output_path)

    if fmt == "rar":
        cmd = ["rar", "a", "-r", "-y"]
        if pwd:
            cmd.append(f"-p{pwd}")
        cmd.extend([abs_output, "*"])
        cwd_dir = source_path if os.path.isdir(source_path) else os.path.dirname(source_path)
    else:
        cmd_fmt = "gzip" if fmt == "gz" else fmt
        # Folder ဖြစ်ပါက folder path တစ်ခုလုံး သို့မဟုတ် ဖိုင်တစ်ခုချင်းစီ ပေးပို့ခြင်း
        cmd = ["7z", "a", f"-t{cmd_fmt}", abs_output]
        
        if os.path.isdir(source_path):
            cwd_dir = source_path
            # folder ထဲရှိ items အားလုံးကို ယူရန်
            cmd.append("*")
        else:
            cwd_dir = os.path.dirname(source_path)
            cmd.append(os.path.basename(source_path))

        cmd.extend(["-y", "-r"])
        
        if pwd and fmt in ["7z", "zip"]:
            cmd.append(f"-p{pwd}")
            if fmt == "7z":
                cmd.append("-mhe=on")

    result = subprocess.run(cmd, cwd=cwd_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        err_msg = (result.stderr or result.stdout or "Unknown 7z error").strip()
        print(f"Archive Error Detail: {err_msg}", flush=True)
        return False, err_msg
        
    return True, ""
