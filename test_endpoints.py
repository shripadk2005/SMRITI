import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

def test_routes():
    client = app.test_client()

    routes_to_test = [
        ('/', 200),
        ('/login', 200),
        ('/register', 200),
        ('/service-worker.js', 200),
        ('/manifest.json', 200),
        ('/api/games', 200)
    ]

    print("Testing public and static routes:")
    for path, expected_status in routes_to_test:
        res = client.get(path)
        assert res.status_code == expected_status, f"Route {path} failed: got {res.status_code}, expected {expected_status}"
        print(f"  ✓ {path} -> {res.status_code}")

    # Test login as Raj Kumar (patient)
    print("\nTesting authentication and authenticated views:")
    login_res = client.post('/api/login', json={'email': 'raj@mindcare.in', 'password': 'patient123'})
    assert login_res.status_code == 200, f"Login failed: {login_res.data}"
    print("  ✓ POST /api/login -> 200 (Patient Raj Kumar authenticated)")

    auth_routes = [
        ('/patient/dashboard', 200),
        ('/memory-vault', 200),
        ('/games', 200),
        ('/games/family-recall', 200),
        ('/games/memory-cards', 200),
        ('/games/object-recall', 200),
        ('/games/pattern-recognition', 200),
        ('/games/attention-game', 200),
        ('/games/routine-recall', 200),
        ('/games/picture-recognition', 200),
        ('/games/emotion-recognition', 200),
        ('/reminders', 200),
        ('/appointments', 200),
        ('/progress', 200),
        ('/familiar-memories', 200),
        ('/api/patient/profile', 200),
        ('/api/patient/progress', 200),
        ('/api/reminders', 200),
        ('/api/appointments', 200),
        ('/api/patient/memories', 200)
    ]

    for path, expected_status in auth_routes:
        res = client.get(path)
        assert res.status_code == expected_status, f"Route {path} failed: got {res.status_code}, expected {expected_status}"
        print(f"  ✓ {path} -> {res.status_code}")

    # Test Personal Memory Creation (Family/Address/Show)
    print("\nTesting Personal Memory Vault APIs:")
    new_mem_payload = {
        'category': 'family',
        'title': 'Pooja Kumar',
        'relationship_or_type': 'Granddaughter',
        'image_url': 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400',
        'details': 'Loves singing Bihu songs and painting.'
    }
    # Test Image File Upload (for familiar persons or shows)
    import io
    print("\nTesting Image Upload API:")
    dummy_file = (io.BytesIO(b"fake-image-bytes-png-header"), 'family_photo.png')
    upload_res = client.post('/api/upload-image', data={'image': dummy_file}, content_type='multipart/form-data')
    assert upload_res.status_code == 201, f"Image upload failed: {upload_res.data}"
    uploaded_url = upload_res.get_json()['url']
    print(f"  ✓ POST /api/upload-image -> 201 (Saved to {uploaded_url})")

    # Test Personal Memory Creation with Uploaded Image
    new_mem_payload = {
        'category': 'family',
        'title': 'Pooja Kumar',
        'relationship_or_type': 'Granddaughter',
        'image_url': uploaded_url,
        'details': 'Loves singing Bihu songs and painting.'
    }
    mem_post_res = client.post('/api/patient/memories', json=new_mem_payload)
    assert mem_post_res.status_code == 201, f"Memory creation failed: {mem_post_res.data}"
    created_mem_id = mem_post_res.get_json()['memory']['id']
    print(f"  ✓ POST /api/patient/memories -> 201 (Created Memory #{created_mem_id} with custom image)")

    # Test Dynamic Personalized Questions Generation
    pq_res = client.get('/api/games/personal-questions')
    assert pq_res.status_code == 200, f"Personal questions failed: {pq_res.data}"
    pq_json = pq_res.get_json()
    assert pq_json.get('success') is True
    assert len(pq_json.get('questions', [])) > 0
    print(f"  ✓ GET /api/games/personal-questions -> 200 ({len(pq_json['questions'])} dynamic questions generated)")

    # Test Emergency SOS Trigger with Registered Caregiver Resolution
    sos_res = client.post('/api/sos', json={'lat': 26.1445, 'lng': 91.7362, 'message': 'Medical assistance needed'})
    assert sos_res.status_code == 200, f"SOS failed: {sos_res.data}"
    sos_json = sos_res.get_json()
    assert sos_json.get('success') is True
    assert 'call_url' in sos_json
    assert 'caregiver_phone' in sos_json
    assert 'caregiver_name' in sos_json
    print(f"  ✓ POST /api/sos -> 200 (Emergency SOS connected to registered caregiver: {sos_json['caregiver_name']} - {sos_json['caregiver_phone']})")

    # Test Memory Deletion
    del_res = client.delete(f'/api/patient/memories/{created_mem_id}')
    assert del_res.status_code == 200, f"Memory delete failed: {del_res.data}"
    print(f"  ✓ DELETE /api/patient/memories/{created_mem_id} -> 200")

    # Test caregiver login & views
    print("\nTesting caregiver views:")
    caregiver_login = client.post('/api/login', json={'email': 'sunita@mindcare.in', 'password': 'caregiver123'})
    assert caregiver_login.status_code == 200
    res = client.get('/caregiver/dashboard')
    assert res.status_code == 200
    print("  ✓ /caregiver/dashboard -> 200")
    res = client.get('/api/caregiver/patients')
    assert res.status_code == 200
    print("  ✓ /api/caregiver/patients -> 200")

    # Test admin login & views
    print("\nTesting admin views:")
    admin_login = client.post('/api/login', json={'email': 'admin@mindcare.in', 'password': 'admin123'})
    assert admin_login.status_code == 200
    res = client.get('/admin/dashboard')
    assert res.status_code == 200
    print("  ✓ /admin/dashboard -> 200")
    res = client.get('/api/admin/analytics')
    assert res.status_code == 200
    print("  ✓ /api/admin/analytics -> 200")

    print("\n🎉 ALL ROUTES AND VIEWS TESTED SUCCESSFULLY WITH ZERO ERRORS!")

if __name__ == '__main__':
    test_routes()
