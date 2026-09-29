import os
import subprocess

DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "")

def extract_archive(archive_path: str, extract_dir: str, password: str = None):
    pwd = password or DEFAULT_PASSWORD
    
    cmd = ["7z", "x", os.path.abspath(archive_path), f"-o{os.path.abspath(extract_dir)}", "-y"]
    if pwd:
        cmd.append(f"-p{pwd}")
    
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # 7z မရပါက unar ဖြင့် အရန်အနေနှင့် စမ်းသပ်ခြင်း
    if result.returncode != 0:
        unar_cmd = ["unar", "-o", os.path.abspath(extract_dir), "-f", os.path.abspath(archive_path)]
        if pwd:
            unar_cmd.extend(["-p", pwd])
        result = subprocess.run(unar_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        err = (result.stderr or result.stdout or "Extraction failed").strip()
        return False, err
    return True, ""

def compress_archive(source_path: str, output_path: str, fmt: str = "7z", password: str = None):
    pwd = password or DEFAULT_PASSWORD
    
    if not os.path.exists(source_path):
        return False, f"Folder/File not found at: {source_path}"

    abs_output = os.path.abspath(output_path)
    
    # Folder ထဲရှိ items များကို စစ်ဆေးခြင်း
    if os.path.isdir(source_path):
        items = os.listdir(source_path)
        if not items:
            return False, "Google Drive မှ ဒေါင်းလုဒ်ဆွဲထားသော folder ထဲတွင် မည်သည့်ဖိုင်မှ မရှိပါ (Folder ဗလာဖြစ်နေသည်)။"
        cwd_dir = source_path
        target_args = items  # list ထဲရှိ file အားလုံးကို pass လုပ်ခြင်း (* မသုံးပါ)
    else:
        cwd_dir = os.path.dirname(source_path)
        target_args = [os.path.basename(source_path)]

    if fmt == "rar":
        cmd = ["rar", "a", "-r", "-y"]
        if pwd:
            cmd.append(f"-p{pwd}")
        cmd.append(abs_output)
        cmd.extend(target_args)
    else:
        cmd_fmt = "gzip" if fmt == "gz" else fmt
        cmd = ["7z", "a", f"-t{cmd_fmt}", abs_output]
        cmd.extend(target_args)
        cmd.extend(["-y", "-r"])
        
        if pwd and fmt in ["7z", "zip"]:
            cmd.append(f"-p{pwd}")
            if fmt == "7z":
                cmd.append("-mhe=on")

    # Command run ခြင်း
    result = subprocess.run(cmd, cwd=cwd_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        err_msg = (result.stderr or result.stdout or f"7z exit code: {result.returncode}").strip()
        return False, err_msg
        
    return True, ""
