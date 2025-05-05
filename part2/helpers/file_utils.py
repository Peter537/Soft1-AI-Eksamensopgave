# helpers/file_utils.py
import requests
import streamlit as st

def check_if_file_exists(token: str, base_url: str):
    url = f"{base_url.rstrip('/')}/api/v1/files/"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    files = resp.json()
    return (len(files) > 0, files)

def send_file(token: str, base_url: str, file_obj):
    url = f"{base_url.rstrip('/')}/api/v1/files/"
    headers = {"Authorization": f"Bearer {token}"}
    content_type = getattr(file_obj, "type", "application/octet-stream")
    files = {"file": (file_obj.name, file_obj, content_type)}
    resp = requests.post(url, headers=headers, files=files)
    resp.raise_for_status()
    return resp.json()

def get_file(token: str, base_url: str, file_id: str):
    url = f"{base_url.rstrip('/')}/api/v1/files/{file_id}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

def delete_file(token: str, base_url: str, file_id: str):
    url = f"{base_url.rstrip('/')}/api/v1/files/{file_id}"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.delete(url, headers=headers)
    return resp.status_code == 200
