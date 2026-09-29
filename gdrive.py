import os
import io
import json
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    token_str = os.getenv("G_TOKEN_JSON")
    if not token_str:
        raise ValueError("G_TOKEN_JSON environment variable is not set!")
    info = json.loads(token_str)
    creds = Credentials.from_authorized_user_info(info, SCOPES)
    return build('drive', 'v3', credentials=creds)

def extract_id_from_url(url_or_id: str) -> str:
    """
    Google Drive file/folder URL သို့မဟုတ် raw ID ထဲမှ သန့်စင်သော ID ကို သီးသန့် ဖြတ်ထုတ်ပေးခြင်း
    """
    clean_str = url_or_id.split('?')[0].split('&')[0]
    match = re.search(r'[-\w]{25,}', clean_str)
    if match:
        return match.group(0)
    return clean_str.rstrip('/').split('/')[-1]

def download_file(service, file_id: str, dest_path: str):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    request = service.files().get_media(fileId=file_id, supportsAllDrives=True)
    with open(dest_path, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request, chunksize=10*1024*1024)
        done = False
        while not done:
            status, done = downloader.next_chunk()

def get_file_metadata(service, file_id: str):
    return service.files().get(
        fileId=file_id, 
        fields="id, name, mimeType, parents", 
        supportsAllDrives=True
    ).execute()

def upload_file(service, local_path: str, parent_id: str, file_name: str = None) -> dict:
    name = file_name or os.path.basename(local_path)
    file_metadata = {
        'name': name,
        'parents': [parent_id]
    }
    media = MediaFileUpload(local_path, resumable=True)
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, name',
        supportsAllDrives=True
    ).execute()
    return file

def download_folder(service, folder_id: str, local_dir: str):
    os.makedirs(local_dir, exist_ok=True)
    page_token = None
    while True:
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            fields="nextPageToken, files(id, name, mimeType)",
            includeItemsFromAllDrives=True,
            supportsAllDrives=True,
            pageSize=1000,
            pageToken=page_token
        ).execute()

        files_list = results.get('files', [])
        for item in files_list:
            item_path = os.path.join(local_dir, item['name'])
            if item['mimeType'] == 'application/vnd.google-apps.folder':
                download_folder(service, item['id'], item_path)
            else:
                download_file(service, item['id'], item_path)

        page_token = results.get('nextPageToken', None)
        if not page_token:
            break

def upload_folder(service, local_dir: str, parent_id: str):
    folder_name = os.path.basename(local_dir.rstrip('/\\'))
    meta = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    created_folder = service.files().create(
        body=meta, 
        fields='id', 
        supportsAllDrives=True
    ).execute()
    new_folder_id = created_folder['id']

    for entry in os.scandir(local_dir):
        if entry.is_dir():
            upload_folder(service, entry.path, new_folder_id)
        elif entry.is_file():
            upload_file(service, entry.path, new_folder_id)
