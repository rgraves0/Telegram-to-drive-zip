import os
import shutil
import tempfile
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import MessageNotModified
import gdrive
import archiver

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

app = Client("gdrive_archiver_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

async def safe_edit(msg: Message, text: str):
    """Telegram Message Not Modified error မတက်စေရန် စစ်ဆေးပြီးမှ edit ပြုလုပ်ခြင်း"""
    try:
        if msg.text != text:
            await msg.edit_text(text)
    except MessageNotModified:
        pass
    except Exception as e:
        print(f"Edit message error: {e}", flush=True)

@app.on_message(filters.command("start"))
async def start_handler(client: Client, message: Message):
    await message.reply_text(
        "👋 **Google Drive Archive Bot မှ ကြိုဆိုပါသည်!**\n\n"
        "**အသုံးပြုနည်း Commands:**\n"
        "1. `/unzip <Drive_File_Link>`\n"
        "   👉 Zip, 7z, Rar, Tar စသည့် archive များကို ဖြည်ပြီး drive ထဲသို့ ပြန်တင်ပေးမည်။\n\n"
        "2. `/zip <Drive_Link> [format]`\n"
        "   👉 Format မထည့်ပါက **7z (Default)** ဖြင့် compress လုပ်ပါမည်။\n"
        "   👉 Supported: `7z`, `zip`, `rar`, `tar`, `gz`"
    )

@app.on_message(filters.command("unzip"))
async def unzip_handler(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("အသုံးပြုပုံ: `/unzip <Drive_File_Link>`")

    status_msg = await message.reply_text("⏳ Drive API နှင့် ချိတ်ဆက်နေပါသည်...")
    temp_dir = tempfile.mkdtemp()

    try:
        service = gdrive.get_drive_service()
        file_id = gdrive.extract_id_from_url(message.command[1])
        
        await safe_edit(status_msg, "📥 ဖိုင်အချက်အလက် ရယူပြီး ဒေါင်းလုဒ်ဆွဲနေပါသည်...")
        meta = gdrive.get_file_metadata(service, file_id)
        local_archive = os.path.join(temp_dir, meta['name'])
        
        gdrive.download_file(service, file_id, local_archive)

        await safe_edit(status_msg, "📦 Archive ကို ဖြည်ထုတ်နေပါသည်...")
        extract_folder = os.path.join(temp_dir, "extracted")
        os.makedirs(extract_folder, exist_ok=True)
        
        success, err_msg = archiver.extract_archive(local_archive, extract_folder)
        if not success:
            err_detail = err_msg[:500] if err_msg else "Password မှားယွင်းခြင်း သို့မဟုတ် archive ပျက်စီးနေခြင်း"
            return await safe_edit(status_msg, f"❌ **Archive ဖြည်ရာတွင် အမှားဖြစ်သွားပါသည်:**\n```\n{err_detail}\n```")

        await safe_edit(status_msg, "📤 Drive / Shared Drive သို့ ပြန်လည်တင်နေပါသည်...")
        parent_id = meta.get('parents', ['root'])[0]
        gdrive.upload_folder(service, extract_folder, parent_id)

        await safe_edit(status_msg, f"✅ **အောင်မြင်ပါသည်!**\n`{meta['name']}` ကို အောင်မြင်စွာ ဖြည်ထုတ်ပြီးပါပြီ။")

    except Exception as e:
        await safe_edit(status_msg, f"❌ **Error:** `{str(e)}`")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

@app.on_message(filters.command("zip"))
async def zip_handler(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("အသုံးပြုပုံ: `/zip <Drive_Link> [format]` (Default format: 7z)")

    fmt = message.command[2].lower() if len(message.command) > 2 else "7z"
    status_msg = await message.reply_text("⏳ Processing စတင်နေပါသည်...")
    temp_dir = tempfile.mkdtemp()

    try:
        service = gdrive.get_drive_service()
        target_id = gdrive.extract_id_from_url(message.command[1])
        meta = gdrive.get_file_metadata(service, target_id)

        await safe_edit(status_msg, "📥 Google Drive မှ ဖိုင်များကို ဒေါင်းလုဒ်ဆွဲနေပါသည်...")
        local_target = os.path.join(temp_dir, meta['name'])

        if meta['mimeType'] == 'application/vnd.google-apps.folder':
            gdrive.download_folder(service, target_id, local_target)
        else:
            gdrive.download_file(service, target_id, local_target)

        await safe_edit(status_msg, f"🔐 `{fmt}` Format ဖြင့် Compress လုပ်နေပါသည်...")
        archive_name = f"{meta['name']}.{fmt}"
        output_archive = os.path.join(temp_dir, archive_name)

        success, err_msg = archiver.compress_archive(local_target, output_archive, fmt=fmt)
        if not success:
            err_detail = err_msg[:500] if err_msg else "CLI execution failed"
            return await safe_edit(status_msg, f"❌ **`{fmt}` archive ချုပ်ရာတွင် အမှားဖြစ်သွားပါသည်:**\n```\n{err_detail}\n```")

        await safe_edit(status_msg, "📤 Shared Drive ထဲသို့ Archive တင်နေပါသည်...")
        parent_id = meta.get('parents', ['root'])[0]
        gdrive.upload_file(service, output_archive, parent_id)

        await safe_edit(status_msg, f"✅ **ပြီးစီးပါပြီ!**\nဖိုင်နာမည်: `{archive_name}`")

    except Exception as e:
        await safe_edit(status_msg, f"❌ **Error:** `{str(e)}`")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    print("Bot is starting...", flush=True)
    app.run()
