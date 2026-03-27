"""End-to-end test for full stack."""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("=" * 60)
    print("1. Testing Health Endpoint")
    print("=" * 60)
    resp = requests.get(f"{BASE_URL}/api/health")
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.json()}")
    return resp.status_code == 200

def test_import(segment_type, description):
    """Test file import with given segment type."""
    print(f"\n{'=' * 60}")
    print(f"2. Testing Import - {description} (segment_type='{segment_type}')")
    print("=" * 60)
    
    # Prepare multipart request
    with open("test_interview.txt", "rb") as f:
        file_content = f.read()
    
    # Build multipart form data manually
    boundary = "----FormBoundary"
    body = []
    
    # Add segment_type field
    body.append(f"--{boundary}".encode())
    body.append(b'Content-Disposition: form-data; name="segment_type"')
    body.append(b"")
    body.append(segment_type.encode())
    
    # Add file field
    body.append(f"--{boundary}".encode())
    body.append(b'Content-Disposition: form-data; name="file"; filename="test_interview.txt"')
    body.append(b"Content-Type: text/plain")
    body.append(b"")
    body.append(file_content)
    
    body.append(f"--{boundary}--".encode())
    
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}"
    }
    
    resp = requests.post(
        f"{BASE_URL}/api/import/file",
        data=b"\r\n".join(body),
        headers=headers
    )
    
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        result = resp.json()
        print(f"Message: {result.get('message')}")
        print(f"Count: {result.get('count')}")
        print(f"Segment Type: {result.get('segment_type')}")
        
        if 'speakers' in result:
            print(f"Speakers: {result.get('speakers')}")
        
        # Show first 2 segments
        segments = result.get('segments', [])
        print(f"\nFirst 2 segments preview:")
        for seg in segments[:2]:
            content = seg['content'][:80].replace('\n', ' ')
            print(f"  [{seg['id']}] {content}...")
        
        if len(segments) > 2:
            print(f"  ... and {len(segments) - 2} more")
        
        return True
    else:
        print(f"Error: {resp.text}")
        return False

def test_list_segments():
    """Test listing all segments."""
    print(f"\n{'=' * 60}")
    print("3. Testing List Segments")
    print("=" * 60)
    
    resp = requests.get(f"{BASE_URL}/api/import/segments")
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        segments = resp.json()
        print(f"Total segments: {len(segments)}")
        return True
    return False

def test_clear_segments():
    """Test clearing all segments."""
    print(f"\n{'=' * 60}")
    print("4. Testing Clear Segments")
    print("=" * 60)
    
    resp = requests.delete(f"{BASE_URL}/api/import/segments")
    print(f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        print(f"Response: {resp.json()}")
        return True
    return False

def main():
    print("\n" + "=" * 60)
    print("END-TO-END FULL STACK TEST")
    print("Backend: http://localhost:8000")
    print("Frontend: http://localhost:5173")
    print("=" * 60)
    
    results = []
    
    # Test health
    results.append(("Health", test_health()))
    
    # Test different segment types
    test_cases = [
        ("paragraph", "Paragraph"),
        ("turn", "Speaker Turn"),
        ("qa", "Q&A Pair"),
    ]
    
    for seg_type, desc in test_cases:
        # Clear before each test
        requests.delete(f"{BASE_URL}/api/import/segments")
        results.append((f"Import-{desc}", test_import(seg_type, desc)))
    
    # List all segments
    results.append(("List Segments", test_list_segments()))
    
    # Clear segments
    results.append(("Clear Segments", test_clear_segments()))
    
    # Summary
    print(f"\n{'=' * 60}")
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed!")

if __name__ == "__main__":
    main()
