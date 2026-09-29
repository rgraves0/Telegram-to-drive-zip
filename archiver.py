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
    
    if os.path.isdir(source_path):
        items = os.listdir(source_path)
        if not items:
            return False, "Google Drive မှ folder ထဲတွင် ဖိုင်မရှိပါ (Folder ဗလာဖြစ်နေသည်)။"
        cwd_dir = source_path
        target_args = items
    else:
        cwd_dir = os.path.dirname(source_path)
        target_args = [os.path.basename(source_path)]

    if fmt == "rar":
        # -m1 = Fastest compression (RAM အနည်းဆုံးသုံးရန်)
        cmd = ["rar", "a", "-m1", "-r", "-y"]
        if pwd:
            cmd.append(f"-p{pwd}")
        cmd.append(abs_output)
        cmd.extend(target_args)
    else:
        cmd_fmt = "gzip" if fmt == "gz" else fmt
        # -mx=1 : Fastest compression (RAM သုံးစွဲမှုကို 10MB - 30MB ဝန်းကျင်သာ ကန့်သတ်ရန်)
        # -mmt=1 : CPU/Thread တစ်ခုတည်းသာ သုံးပြီး Memory spike မဖြစ်စေရန်
        cmd = ["7z", "a", f"-t{cmd_fmt}", "-mx=1", "-mmt=1", abs_output]
        cmd.extend(target_args)
        cmd.extend(["-y", "-r"])
        
        if pwd and fmt in ["7z", "zip"]:
            cmd.append(f"-p{pwd}")
            if fmt == "7z":
                cmd.append("-mhe=on")

    result = subprocess.run(cmd, cwd=cwd_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        err_msg = (result.stderr or result.stdout or f"7z exit code: {result.returncode}").strip()
        return False, err_msg
        
    return True, ""
