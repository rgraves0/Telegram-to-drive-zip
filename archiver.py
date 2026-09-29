import os
import subprocess

DEFAULT_PASSWORD = os.getenv("DEFAULT_PASSWORD", "")

def extract_archive(archive_path: str, extract_dir: str, password: str = None) -> bool:
    pwd = password or DEFAULT_PASSWORD
    
    # 7z ဖြင့် အရင် ဖြည်ကြည့်မည်
    cmd = ["7z", "x", archive_path, f"-o{extract_dir}", "-y"]
    if pwd:
        cmd.append(f"-p{pwd}")
    
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # 7z မရပါက unar ဖြင့် စမ်းမည်
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
    
    # Folder ဖြစ်နေပါက အထဲက ဖိုင်အားလုံးပါအောင် Path ညှိခြင်း
    target = os.path.join(source_path, "*") if os.path.isdir(source_path) else source_path

    if fmt == "rar":
        cmd = ["rar", "a", "-r", "-y"]
        if pwd:
            cmd.append(f"-p{pwd}")
        cmd.extend([output_path, target])
    else:
        # 7z, zip, tar, gzip စသည်တို့အတွက်
        # gzip/gz ဖြစ်ပါက tar.gz ပုံစံမျိုး သို့မဟုတ် format အမှန် ညွှန်ပေးခြင်း
        cmd_fmt = "gzip" if fmt == "gz" else fmt
        cmd = ["7z", "a", f"-t{cmd_fmt}", output_path, target, "-y", "-r"]
        
        # Password encryption (7z နှင့် zip အတွက်သာ)
        if pwd and fmt in ["7z", "zip"]:
            cmd.append(f"-p{pwd}")
            if fmt == "7z":
                cmd.append("-mhe=on")

    # Command ကို run ပြီး error ရှိပါက console log ထုတ်ကြည့်ရန်
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        print(f"Compression Error Log: {result.stderr}")
        return False
    return True
