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

processing_users = set()

async def safe_edit(msg: Message, text: str):
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
        "   👉 Archive ကို ဖြည်ပြီး မူရင်း folder သို့ တင်ပေးမည်။\n\n"
        "2. `/zip <Drive_Link> [format]`\n"
        "   👉 Folder ကို compress လုပ်ပြီး မူရင်း folder အား အလိုအလျောက် trash ထဲ ရွှေ့ပေးမည်။\n"
        "   👉 Supported: `7z` (Default), `zip`, `rar`, `tar`, `gz`"
    )

@app.on_message(filters.command("zip"))
async def zip_handler(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in processing_users:
        return

    if len(message.command) < 2:
        return await message.reply_text("အသုံးပြုပုံ: `/zip <Drive_Link> [format]` (Default: 7z)")

    processing_users.add(user_id)
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

        # Archive တင်ပြီးစီးပါက မူရင်း folder/file ကို Trash ထဲ ရွှေ့ခြင်း
        await safe_edit(status_msg, "🗑️ မူရင်း Folder အား Drive ထဲမှ ရှင်းလင်းနေပါသည်...")
        try:
            gdrive.trash_item(service, target_id)
            trash_status = "(မူရင်း Folder ကို Trash သို့ ရွှေ့ပြီးပါပြီ)"
        except Exception as e:
            trash_status = f"(မူရင်းဖျက်ရာတွင် အမှားရှိ: {e})"

        await safe_edit(status_msg, f"✅ **ပြီးစီးပါပြီ!**\nဖိုင်နာမည်: `{archive_name}`\n{trash_status}")

    except Exception as e:
        await safe_edit(status_msg, f"❌ **Error:** `{str(e)}`")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
        processing_users.discard(user_id)

if __name__ == "__main__":
    print("Bot is starting...", flush=True)
    app.run()
