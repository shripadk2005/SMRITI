"""
MINDCARE NER – Automated Test Suite
Verifies application factory, database models, scikit-learn AI engine,
REST APIs, caregiver telemetry, and offline synchronization.
"""

import sys
import os
import unittest
from datetime import datetime, date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from models import db
from models.user import User
from models.patient import Patient
from models.caregiver import Caregiver
from models.game import Game, GameResult
from models.reminder import Reminder, Appointment
from models.alert import Alert, SyncQueue
from models.memory import PersonalMemory
from ai.adaptive_engine import get_ai_engine, calculate_next_difficulty
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret'

class MindCareTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            self._seed_test_user()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _seed_test_user(self):
        user = User(
            name="Raj Kumar",
            email="raj.test@mindcare.in",
            phone="9864199887",
            role="patient",
            language="en"
        )
        user.set_password("patient123")
        db.session.add(user)
        db.session.flush()

        patient = Patient(
            user_id=user.id,
            emergency_contact="Sunita Sharma - 9435011223",
            region="Assam"
        )
        db.session.add(patient)
        db.session.commit()
        self.patient_id = patient.id
        self.user_id = user.id

    def test_user_password_hashing(self):
        with self.app.app_context():
            user = db.session.get(User, self.user_id)
            self.assertTrue(user.check_password("patient123"))
            self.assertFalse(user.check_password("wrongpassword"))

    def test_ai_adaptive_engine(self):
        engine = get_ai_engine()
        # High accuracy -> should upgrade
        high_res = engine.evaluate({'accuracy': 95.0, 'completion_time': 15.0, 'attempts': 1, 'difficulty': 'EASY'})
        self.assertIn(high_res['difficulty'], ['MEDIUM', 'HARD'])
        self.assertIn("personalized", high_res['message'])

        # Low accuracy -> should demote or stay EASY
        low_res = engine.evaluate({'accuracy': 35.0, 'completion_time': 80.0, 'attempts': 4, 'difficulty': 'MEDIUM'})
        self.assertEqual(low_res['difficulty'], 'EASY')

        # Entry point function test
        self.assertEqual(calculate_next_difficulty({'accuracy': 95.0, 'completion_time': 12.0, 'attempts': 1, 'difficulty': 'EASY'}), 'MEDIUM')

    def test_api_login(self):
        resp = self.client.post('/api/login', json={
            'email': 'raj.test@mindcare.in',
            'password': 'patient123'
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['user']['name'], 'Raj Kumar')

    def test_api_game_result_and_ai(self):
        # First login
        self.client.post('/api/login', json={
            'email': 'raj.test@mindcare.in',
            'password': 'patient123'
        })

        resp = self.client.post('/api/games/result', json={
            'patient_id': self.patient_id,
            'game_slug': 'memory-cards',
            'score': 88,
            'accuracy': 92.0,
            'completion_time': 24.5,
            'attempts': 1,
            'difficulty': 'EASY'
        })
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertIn('ai_difficulty', data)
        self.assertIn('result', data)

    def test_api_reminders_crud(self):
        self.client.post('/api/login', json={
            'email': 'raj.test@mindcare.in',
            'password': 'patient123'
        })

        # Create
        create_resp = self.client.post('/api/reminders', json={
            'patient_id': self.patient_id,
            'type': 'medicine',
            'title': 'Morning Tablet',
            'description': '1 tablet after food',
            'reminder_time': '09:00 AM',
            'frequency': 'Daily'
        })
        self.assertEqual(create_resp.status_code, 201)
        rem_id = create_resp.get_json()['reminder']['id']

        # Toggle status
        toggle_resp = self.client.post(f'/api/reminders/{rem_id}/toggle')
        self.assertEqual(toggle_resp.status_code, 200)
        self.assertEqual(toggle_resp.get_json()['reminder']['status'], 'completed')

    def test_offline_sync_api(self):
        resp = self.client.post('/api/sync', json={
            'patient_id': self.patient_id,
            'items': [
                {
                    'type': 'game_result',
                    'data': {
                        'game_slug': 'memory-cards',
                        'score': 90,
                        'accuracy': 95.0,
                        'completion_time': 20.0,
                        'attempts': 1,
                        'difficulty': 'EASY'
                    }
                }
            ]
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['synced_results'], 1)

    def test_personal_memory_vault_and_ai_questions(self):
        # Authenticate
        self.client.post('/api/login', json={
            'email': 'raj.test@mindcare.in',
            'password': 'patient123'
        })

        # Add family memory
        add_resp = self.client.post('/api/patient/memories', json={
            'category': 'family',
            'title': 'Aarav Sharma',
            'relationship_or_type': 'Grandson',
            'image_url': 'https://images.unsplash.com/photo-1544717305-2782549b5136?w=400',
            'details': 'Loves playing chess and drawing.'
        })
        self.assertEqual(add_resp.status_code, 201)
        mem_data = add_resp.get_json()
        self.assertTrue(mem_data['success'])
        mem_id = mem_data['memory']['id']

        # Add show memory
        self.client.post('/api/patient/memories', json={
            'category': 'favorite_show',
            'title': 'Ramayan',
            'relationship_or_type': 'TV Serial',
            'details': 'Watched together on Sunday mornings.'
        })

        # Get memories list
        list_resp = self.client.get('/api/patient/memories')
        self.assertEqual(list_resp.status_code, 200)
        memories = list_resp.get_json()
        self.assertGreaterEqual(len(memories), 2)

        # Dynamic game questions generation based on user's personal memories
        q_resp = self.client.get('/api/games/personal-questions')
        self.assertEqual(q_resp.status_code, 200)
        q_data = q_resp.get_json()
        self.assertTrue(q_data['success'])
        self.assertGreaterEqual(len(q_data['questions']), 2)

        # Verify a question mentions the added family member or show
        question_texts = [q['question'] + ' ' + q.get('correct', '') for q in q_data['questions']]
        has_relevant = any('Aarav' in t or 'Ramayan' in t for t in question_texts)
        self.assertTrue(has_relevant)

        # Clean up delete
        del_resp = self.client.delete(f'/api/patient/memories/{mem_id}')
        self.assertEqual(del_resp.status_code, 200)

    def test_image_upload_api(self):
        import io
        # Must be logged in
        self.client.post('/api/login', json={
            'email': 'raj.test@mindcare.in',
            'password': 'patient123'
        })
        dummy_file = (io.BytesIO(b"fake-image-bytes-png"), 'test_pic.png')
        resp = self.client.post('/api/upload-image', data={'image': dummy_file}, content_type='multipart/form-data')
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertTrue(data['success'])
        self.assertTrue(data['url'].startswith('/static/uploads/'))

    def test_emergency_sos_alert(self):
        # Trigger SOS alert
        sos_resp = self.client.post('/api/sos', json={
            'location': 'Zoo Road, Guwahati, Assam',
            'note': 'Test emergency triggered'
        })
        self.assertEqual(sos_resp.status_code, 200)
        sos_data = sos_resp.get_json()
        self.assertTrue(sos_data['success'])
        self.assertIn('112', str(sos_data['emergency_numbers']))
        self.assertIn('caregiver_name', sos_data)
        self.assertIn('caregiver_phone', sos_data)
        self.assertTrue(sos_data['call_url'].startswith('tel:'))

        # Verify alert stored in DB
        with self.app.app_context():
            sos_alert = Alert.query.filter_by(alert_type='emergency_sos').first()
            self.assertIsNotNone(sos_alert)
            self.assertIn('CRITICAL SOS ALERT', sos_alert.message)

if __name__ == '__main__':
    unittest.main()
