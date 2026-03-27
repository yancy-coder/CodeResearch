"""Debug test for multipart form."""
import requests

BASE_URL = "http://localhost:8000"

# Test 1: Simple form data
print("Test 1: Simple form data")
resp = requests.post(
    f"{BASE_URL}/api/import/file",
    data={"segment_type": "turn"},
    files={"file": ("test.txt", b"Line 1\n\nLine 2\n\nLine 3", "text/plain")}
)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.text[:500]}")

# Test 2: With explicit content-type
print("\nTest 2: Check what requests is sending")
import io
from urllib.parse import urlencode

# Use prepared request to see what's being sent
req = requests.Request(
    'POST',
    f"{BASE_URL}/api/import/file",
    data={"segment_type": "qa"},
    files={"file": ("test.txt", b"Content here", "text/plain")}
)
prepared = req.prepare()
print(f"Content-Type: {prepared.headers.get('Content-Type')}")
print(f"Body preview: {prepared.body[:200] if prepared.body else 'None'}...")
