#!/usr/bin/env python3
import io
import os
import time
import uuid
from pathlib import Path

import requests
from PIL import Image

BASE_URL = "http://127.0.0.1:8000"
UPLOADS_DIR = Path("uploads")


def make_png_bytes(width=10, height=10, color=(255, 0, 0, 255)) -> bytes:
    img = Image.new("RGBA", (width, height), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def make_large_png_bytes(target_mb: int = 3) -> bytes:
    # Create a large image to exceed 2MB (target ~3MB)
    size = 2000
    img = Image.new("RGB", (size, size), (123, 222, 111))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    data = buf.getvalue()
    # If still not large enough, repeat data
    while len(data) < target_mb * 1024 * 1024:
        data += data
    return data


def login_admin():
    resp = requests.post(f"{BASE_URL}/auth/login", json={"name": "admin", "password": "admin123"})
    resp.raise_for_status()
    data = resp.json()
    return data["access_token"], data.get("refresh_token")


def create_employee(token: str, name: str, email: str) -> dict:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"Name": name, "Email": email}
    resp = requests.post(f"{BASE_URL}/employees/", headers=headers, json=payload)
    resp.raise_for_status()
    return resp.json()


def upload_image(token: str, emp_id: int, bytes_data: bytes, filename: str, content_type: str = "image/png") -> requests.Response:
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": (filename, io.BytesIO(bytes_data), content_type)}
    return requests.post(f"{BASE_URL}/employees/{emp_id}/image", headers=headers, files=files)


def get_employee(token: str, emp_id: int) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/employees/{emp_id}", headers=headers)
    resp.raise_for_status()
    return resp.json()


def get_image_info(token: str, emp_id: int) -> requests.Response:
    headers = {"Authorization": f"Bearer {token}"}
    return requests.get(f"{BASE_URL}/employees/{emp_id}/image", headers=headers)


def delete_image(token: str, emp_id: int) -> requests.Response:
    headers = {"Authorization": f"Bearer {token}"}
    return requests.delete(f"{BASE_URL}/employees/{emp_id}/image", headers=headers)


def delete_employee(token: str, emp_id: int) -> None:
    headers = {"Authorization": f"Bearer {token}"}
    requests.delete(f"{BASE_URL}/employees/{emp_id}", headers=headers)


def main():
    print("🔍 Phase 6: Backend image flow tests")

    # Health
    r = requests.get(f"{BASE_URL}/")
    print(f"✅ Backend health: {r.status_code}")

    token, _ = login_admin()
    print("✅ Login successful")

    unique = uuid.uuid4().hex[:8]
    emp_a = create_employee(token, f"Image Test A {unique}", f"image.a.{unique}@example.com")
    emp_b = create_employee(token, f"Image Test B {unique}", f"image.b.{unique}@example.com")
    print(f"✅ Created employees: {emp_a['emp_id']} and {emp_b['emp_id']}")

    try:
        # Upload small valid PNG to A
        png_bytes = make_png_bytes()
        resp = upload_image(token, emp_a["emp_id"], png_bytes, "test.png")
        assert resp.status_code == 200, f"Valid PNG upload failed: {resp.status_code} {resp.text}"
        a_after = get_employee(token, emp_a["emp_id"])
        print(f"✅ Uploaded PNG to A; image_hash={a_after.get('image_hash')}")

        # Upload same PNG to B - should dedupe (same hash) but alias different
        resp = upload_image(token, emp_b["emp_id"], png_bytes, "duplicate.png")
        assert resp.status_code == 200, f"Duplicate PNG upload failed: {resp.status_code} {resp.text}"
        b_after = get_employee(token, emp_b["emp_id"])
        print(f"✅ Uploaded same PNG to B; image_hash={b_after.get('image_hash')}")

        assert a_after.get("image_hash") == b_after.get("image_hash"), "Dedup failed: hashes differ"
        print("✅ Dedup confirmed: identical hashes for same image")

        # Canonical file existence
        image_hash = a_after.get("image_hash")
        if image_hash:
            canonical_path = UPLOADS_DIR / f"{image_hash}.png"
            assert canonical_path.exists(), f"Canonical file missing: {canonical_path}"
            print(f"✅ Canonical file exists: {canonical_path}")

        # Alias fetch works
        r_alias = requests.get(f"{BASE_URL}/uploads/{emp_a['emp_id']}.png")
        assert r_alias.status_code in (200, 304), f"Alias fetch failed: {r_alias.status_code}"
        print("✅ Alias fetch works for A")

        # Image info endpoint
        info_resp = get_image_info(token, emp_a["emp_id"])
        assert info_resp.status_code == 200, f"Image info failed: {info_resp.status_code}"
        print("✅ Image info endpoint returns 200")

        # Reject >2MB
        large_png = make_large_png_bytes(3)
        too_big_resp = upload_image(token, emp_a["emp_id"], large_png, "big.png")
        assert too_big_resp.status_code in (400, 413), f"Too-large upload not rejected: {too_big_resp.status_code}"
        print("✅ Too-large image rejected")

        # Reject non-image
        text_bytes = b"this is not an image"
        bad_type_resp = upload_image(token, emp_a["emp_id"], text_bytes, "bad.txt", content_type="text/plain")
        assert bad_type_resp.status_code in (400, 415), f"Non-image upload not rejected: {bad_type_resp.status_code}"
        print("✅ Non-image upload rejected")

        # Delete image and verify alias removed, canonical kept
        del_resp = delete_image(token, emp_a["emp_id"])
        assert del_resp.status_code == 200, f"Delete image failed: {del_resp.status_code}"
        alias_path = UPLOADS_DIR / f"{emp_a['emp_id']}.png"
        assert not alias_path.exists(), "Alias file still exists after deletion"
        print("✅ Alias removed after delete")

        # After delete, info returns 404 and alias fetch 404
        info_after_del = get_image_info(token, emp_a["emp_id"])
        assert info_after_del.status_code == 404, f"Image info after delete should be 404, got {info_after_del.status_code}"
        alias_after_del = requests.get(f"{BASE_URL}/uploads/{emp_a['emp_id']}.png")
        assert alias_after_del.status_code in (404, 400), f"Alias still fetchable after delete: {alias_after_del.status_code}"
        print("✅ Image endpoints reflect deletion")

    finally:
        # Cleanup - delete test employees
        delete_employee(token, emp_a["emp_id"])
        delete_employee(token, emp_b["emp_id"])
        print("🧹 Cleanup complete (employees deleted)")

    print("\n🎯 Phase 6 backend tests completed successfully")


if __name__ == "__main__":
    main()
