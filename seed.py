"""
MINDCARE NER – Database Seeder
Populates realistic demonstration data for Smart India Hackathon presentation:
- 3 Elderly Patients (with North-Eastern locations & emergency contacts)
- 2 Caregivers (linked to patients)
- 1 Healthcare Officer / Admin
- 7 Cognitive Games
- Historical Game Telemetry for charts & AI difficulty demonstrations
- Reminders (Medicine, Hydration, Daily Activities)
- Medical Appointments
- Caregiver Supportive Alerts
"""

from datetime import datetime, date, timedelta
from app import create_app
from models import db
from models.user import User
from models.patient import Patient
from models.caregiver import Caregiver
from models.game import Game, GameResult
from models.reminder import Reminder, Appointment
from models.alert import Alert, SyncQueue
from models.memory import PersonalMemory

app = create_app()

def seed_database():
    with app.app_context():
        print("🌱 Seeding MindCare NER database...")
        db.drop_all()
        db.create_all()

        # 1. Create Default Games
        games_data = [
            {
                'slug': 'memory-cards',
                'name': 'Memory Cards',
                'category': 'Memory',
                'difficulty': 'EASY',
                'description': 'Match pairs of familiar North-Eastern cultural symbols (Tea Cup, Japi, Rice Bowl, Hornbill).',
                'icon': 'fa-clone'
            },
            {
                'slug': 'object-recall',
                'name': 'Remember the Objects',
                'category': 'Memory',
                'difficulty': 'EASY',
                'description': 'Memorize familiar household and cultural objects for 10 seconds, then recall them.',
                'icon': 'fa-eye'
            },
            {
                'slug': 'pattern-recognition',
                'name': 'Pattern Recognition',
                'category': 'Pattern',
                'difficulty': 'MEDIUM',
                'description': 'Identify the next logical shape or color in a sequence.',
                'icon': 'fa-shapes'
            },
            {
                'slug': 'attention-game',
                'name': 'Focus & Attention',
                'category': 'Attention',
                'difficulty': 'EASY',
                'description': 'Find the target object among visual distractors as quickly and accurately as possible.',
                'icon': 'fa-bullseye'
            },
            {
                'slug': 'routine-recall',
                'name': 'Daily Routine Recall',
                'category': 'Daily Routine',
                'difficulty': 'EASY',
                'description': 'Recall your sequential morning, afternoon, and evening activities in order.',
                'icon': 'fa-calendar-check'
            },
            {
                'slug': 'picture-recognition',
                'name': 'Familiar Picture Recognition',
                'category': 'Recognition',
                'difficulty': 'EASY',
                'description': 'Recognize familiar NER heritage items, tea gardens, and traditional musical instruments.',
                'icon': 'fa-image'
            },
            {
                'slug': 'emotion-recognition',
                'name': 'Emotional Perception',
                'category': 'Emotional Recognition',
                'difficulty': 'EASY',
                'description': 'Look at friendly expressions and choose how the person feels in a calming environment.',
                'icon': 'fa-smile'
            },
            {
                'slug': 'family-recall',
                'name': 'Who Is This? (Family Recall)',
                'category': 'Personal Memory',
                'difficulty': 'EASY',
                'description': 'Recognize your family members, your home address, and favorite TV serials from your personal memory vault.',
                'icon': 'fa-people-roof'
            }
        ]

        games_dict = {}
        for gd in games_data:
            g = Game(**gd)
            db.session.add(g)
            db.session.flush()
            games_dict[g.slug] = g

        # 2. Create Admin / Healthcare Worker
        admin_user = User(
            name='Dr. Ananya Baruah',
            email='admin@mindcare.in',
            phone='9864012345',
            age=42,
            gender='Female',
            role='admin',
            language='en'
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)

        # 3. Create Caregivers
        caregiver_user_1 = User(
            name='Sunita Sharma',
            email='sunita@mindcare.in',
            phone='9435011223',
            age=34,
            gender='Female',
            role='caregiver',
            language='as'
        )
        caregiver_user_1.set_password('caregiver123')
        db.session.add(caregiver_user_1)
        db.session.flush()

        caregiver_1 = Caregiver(
            user_id=caregiver_user_1.id,
            relationship_to_patient='Daughter & Primary Caregiver'
        )
        db.session.add(caregiver_1)
        db.session.flush()

        caregiver_user_2 = User(
            name='David Lyngdoh',
            email='david@mindcare.in',
            phone='9774055667',
            age=39,
            gender='Male',
            role='caregiver',
            language='kha'
        )
        caregiver_user_2.set_password('caregiver123')
        db.session.add(caregiver_user_2)
        db.session.flush()

        caregiver_2 = Caregiver(
            user_id=caregiver_user_2.id,
            relationship_to_patient='Elder Care Nurse'
        )
        db.session.add(caregiver_2)
        db.session.flush()

        # 4. Create 3 Elderly Patients
        patient_user_1 = User(
            name='Raj Kumar',
            email='raj@mindcare.in',
            phone='9864199887',
            age=74,
            gender='Male',
            role='patient',
            language='en'
        )
        patient_user_1.set_password('patient123')
        db.session.add(patient_user_1)
        db.session.flush()

        patient_1 = Patient(
            user_id=patient_user_1.id,
            caregiver_id=caregiver_1.id,
            emergency_contact='Sunita Sharma (Daughter) - 9435011223',
            region='Assam'
        )
        db.session.add(patient_1)
        db.session.flush()

        patient_user_2 = User(
            name='Maya Devi',
            email='maya@mindcare.in',
            phone='9436122334',
            age=68,
            gender='Female',
            role='patient',
            language='hi'
        )
        patient_user_2.set_password('patient123')
        db.session.add(patient_user_2)
        db.session.flush()

        patient_2 = Patient(
            user_id=patient_user_2.id,
            caregiver_id=caregiver_1.id,
            emergency_contact='Ramesh Chandra (Son) - 9436122335',
            region='Meghalaya'
        )
        db.session.add(patient_2)
        db.session.flush()

        patient_user_3 = User(
            name='Tashi Norbu',
            email='tashi@mindcare.in',
            phone='9862144556',
            age=72,
            gender='Male',
            role='patient',
            language='en'
        )
        patient_user_3.set_password('patient123')
        db.session.add(patient_user_3)
        db.session.flush()

        patient_3 = Patient(
            user_id=patient_user_3.id,
            caregiver_id=caregiver_2.id,
            emergency_contact='Pema Norbu (Brother) - 9862144557',
            region='Sikkim'
        )
        db.session.add(patient_3)
        db.session.flush()

        # User's Personal Account
        patient_user_shripad = User(
            name='Raj Kumar',
            email='shripadk2005@gmail.com',
            phone='9864199887',
            age=74,
            gender='Male',
            role='patient',
            language='en'
        )
        patient_user_shripad.set_password('patient123')
        db.session.add(patient_user_shripad)
        db.session.flush()

        patient_shripad = Patient(
            user_id=patient_user_shripad.id,
            caregiver_id=caregiver_1.id,
            emergency_contact='Sunita Sharma (Daughter) - 9435011223',
            region='Assam'
        )
        db.session.add(patient_shripad)
        db.session.flush()

        # 5. Seed Historical Game Results (for Raj Kumar across past 7 days)
        now = datetime.now()
        history_presets = [
            # 6 days ago
            (6, 'memory-cards', 70, 75.0, 42.5, 2, 'EASY'),
            (6, 'routine-recall', 80, 85.0, 30.0, 1, 'EASY'),
            # 5 days ago
            (5, 'object-recall', 72, 75.0, 38.0, 2, 'EASY'),
            (5, 'pattern-recognition', 68, 70.0, 45.0, 2, 'EASY'),
            # 4 days ago
            (4, 'memory-cards', 75, 80.0, 35.0, 1, 'EASY'),
            (4, 'attention-game', 74, 78.0, 32.0, 1, 'EASY'),
            # 3 days ago
            (3, 'emotion-recognition', 85, 90.0, 25.0, 1, 'EASY'),
            (3, 'picture-recognition', 80, 85.0, 28.0, 1, 'EASY'),
            # 2 days ago
            (2, 'memory-cards', 82, 88.0, 29.0, 1, 'MEDIUM'),
            (2, 'object-recall', 78, 80.0, 33.0, 1, 'EASY'),
            # 1 day ago
            (1, 'pattern-recognition', 85, 90.0, 27.0, 1, 'MEDIUM'),
            (1, 'routine-recall', 90, 95.0, 20.0, 1, 'EASY'),
            # Today
            (0, 'memory-cards', 88, 92.0, 22.0, 1, 'MEDIUM'),
            (0, 'attention-game', 85, 88.0, 24.0, 1, 'EASY')
        ]

        for days_ago, slug, score, accuracy, completion_time, attempts, diff in history_presets:
            played_dt = now - timedelta(days=days_ago, hours=2)
            gr = GameResult(
                patient_id=patient_1.id,
                game_id=games_dict[slug].id,
                score=score,
                accuracy=accuracy,
                completion_time=completion_time,
                attempts=attempts,
                difficulty=diff,
                played_at=played_dt
            )
            db.session.add(gr)

            # Also seed for patient_shripad
            gr_shripad = GameResult(
                patient_id=patient_shripad.id,
                game_id=games_dict[slug].id,
                score=score,
                accuracy=accuracy,
                completion_time=completion_time,
                attempts=attempts,
                difficulty=diff,
                played_at=played_dt
            )
            db.session.add(gr_shripad)

        # Also add some results for Maya and Tashi
        for p in [patient_2, patient_3]:
            for d in range(3):
                gr = GameResult(
                    patient_id=p.id,
                    game_id=games_dict['memory-cards'].id,
                    score=75 + d * 3,
                    accuracy=80.0 + d * 4,
                    completion_time=32.0 - d * 2,
                    attempts=1,
                    difficulty='EASY',
                    played_at=now - timedelta(days=d, hours=3)
                )
                db.session.add(gr)

        # 6. Seed Reminders for Raj Kumar
        today = date.today()
        reminders_data = [
            {
                'patient_id': patient_1.id,
                'type': 'medicine',
                'title': 'Morning Blood Pressure Tablet',
                'description': 'Amlodipine 5mg with a full glass of warm water after breakfast.',
                'reminder_time': '08:30 AM',
                'frequency': 'Daily',
                'status': 'completed',
                'date_scheduled': today,
                'completed_at': now - timedelta(hours=3)
            },
            {
                'patient_id': patient_1.id,
                'type': 'hydration',
                'title': 'Mid-Morning Hydration',
                'description': 'Drink 1 fresh glass of clean water 💧',
                'reminder_time': '10:30 AM',
                'frequency': 'Daily',
                'status': 'completed',
                'date_scheduled': today,
                'completed_at': now - timedelta(hours=1)
            },
            {
                'patient_id': patient_1.id,
                'type': 'medicine',
                'title': 'Memory Support Vitamin',
                'description': 'Vitamin B-Complex tablet with lunch.',
                'reminder_time': '01:30 PM',
                'frequency': 'Daily',
                'status': 'pending',
                'date_scheduled': today
            },
            {
                'patient_id': patient_1.id,
                'type': 'activity',
                'title': 'Gentle Garden Walk',
                'description': '15-minute relaxing stroll in the home garden or veranda.',
                'reminder_time': '05:00 PM',
                'frequency': 'Daily',
                'status': 'pending',
                'date_scheduled': today
            },
            {
                'patient_id': patient_1.id,
                'type': 'medicine',
                'title': 'Night Heart Health Medicine',
                'description': 'Atorvastatin 10mg before bedtime.',
                'reminder_time': '09:00 PM',
                'frequency': 'Daily',
                'status': 'pending',
                'date_scheduled': today
            }
        ]

        for rd in reminders_data:
            rem = Reminder(**rd)
            db.session.add(rem)
            # Also for patient_shripad
            rd_shripad = dict(rd)
            rd_shripad['patient_id'] = patient_shripad.id
            db.session.add(Reminder(**rd_shripad))

        # 7. Seed Appointments
        app1 = Appointment(
            patient_id=patient_1.id,
            doctor='Dr. Hemen Hazarika (Neurologist)',
            hospital='Guwahati Neurological Care Institute, Assam',
            appointment_date=(today + timedelta(days=4)).strftime('%Y-%m-%d'),
            appointment_time='10:30 AM',
            notes='Quarterly routine cognitive checkup and blood pressure review.',
            status='scheduled'
        )
        db.session.add(app1)

        app_shripad = Appointment(
            patient_id=patient_shripad.id,
            doctor='Dr. Hemen Hazarika (Neurologist)',
            hospital='Guwahati Neurological Care Institute, Assam',
            appointment_date=(today + timedelta(days=4)).strftime('%Y-%m-%d'),
            appointment_time='10:30 AM',
            notes='Quarterly routine cognitive checkup and blood pressure review.',
            status='scheduled'
        )
        db.session.add(app_shripad)

        app2 = Appointment(
            patient_id=patient_2.id,
            doctor='Dr. Patricia Shylla',
            hospital='Nazareth Hospital, Shillong',
            appointment_date=(today + timedelta(days=7)).strftime('%Y-%m-%d'),
            appointment_time='11:15 AM',
            notes='Eye checkup and routine health evaluation.',
            status='scheduled'
        )
        db.session.add(app2)

        # 8. Seed Caregiver Alerts
        alerts_data = [
            {
                'patient_id': patient_1.id,
                'caregiver_id': caregiver_1.id,
                'alert_type': 'missed_medicine',
                'message': 'Patient Raj Kumar missed the 09:00 PM bedtime medicine yesterday. Follow up recommended.',
                'status': 'unread',
                'created_at': now - timedelta(hours=14)
            },
            {
                'patient_id': patient_1.id,
                'caregiver_id': caregiver_1.id,
                'alert_type': 'appointment',
                'message': 'Upcoming Neurologist appointment with Dr. Hemen Hazarika in 4 days.',
                'status': 'read',
                'created_at': now - timedelta(days=1)
            },
            {
                'patient_id': patient_2.id,
                'caregiver_id': caregiver_1.id,
                'alert_type': 'low_engagement',
                'message': 'Maya Devi has not engaged with cognitive exercises today. Friendly prompt suggested.',
                'status': 'unread',
                'created_at': now - timedelta(hours=5)
            }
        ]

        for ad in alerts_data:
            alt = Alert(**ad)
            db.session.add(alt)

        # 9. Seed Personal Memory Vault (Family, Addresses, Favorite Shows)
        memories_template = [
            {
                'category': 'family',
                'title': 'Sunita Sharma',
                'relationship_or_type': 'Daughter',
                'image_url': 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400',
                'details': 'Daughter who visits every Sunday with home-cooked Assam tea & meals.'
            },
            {
                'category': 'family',
                'title': 'Aarav Sharma',
                'relationship_or_type': 'Grandson',
                'image_url': 'https://images.unsplash.com/photo-1544717305-2782549b5136?w=400',
                'details': 'Grandson in 5th grade at St. Mary’s School. Loves chess and stories.'
            },
            {
                'category': 'family',
                'title': 'Meera Devi',
                'relationship_or_type': 'Late Wife',
                'image_url': 'https://images.unsplash.com/photo-1567532939604-b6b5b0db2604?w=400',
                'details': 'Beloved wife married in Guwahati in 1978. Loved gardening yellow roses.'
            },
            {
                'category': 'address',
                'title': 'Zoo Road Residence',
                'relationship_or_type': 'Home Address',
                'image_url': 'https://images.unsplash.com/photo-1518780664697-55e3ad937233?w=400',
                'details': 'House No. 42, Zoo Narengi Road, Guwahati, Assam 781024'
            },
            {
                'category': 'favorite_show',
                'title': 'Ramayan',
                'relationship_or_type': 'TV Serial',
                'image_url': 'https://images.unsplash.com/photo-1522869635100-9f4c5e86aa37?w=400',
                'details': 'Classic Ramanand Sagar serial watched together every Sunday morning.'
            },
            {
                'category': 'favorite_show',
                'title': 'Brahmaputra Valley Folk Songs',
                'relationship_or_type': 'Music & Radio',
                'image_url': 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=400',
                'details': 'Traditional folk tunes on All India Radio Guwahati.'
            }
        ]

        # Add memories for patient_1 and patient_shripad
        for p_id in [patient_1.id, patient_shripad.id]:
            for mem_data in memories_template:
                mem = PersonalMemory(
                    patient_id=p_id,
                    category=mem_data['category'],
                    title=mem_data['title'],
                    relationship_or_type=mem_data['relationship_or_type'],
                    image_url=mem_data['image_url'],
                    details=mem_data['details']
                )
                db.session.add(mem)

        db.session.commit()
        print("✅ SMRITI database successfully seeded!")
        print(f"   - Users: {User.query.count()}")
        print(f"   - Patients: {Patient.query.count()}")
        print(f"   - Caregivers: {Caregiver.query.count()}")
        print(f"   - Games: {Game.query.count()}")
        print(f"   - Game Results: {GameResult.query.count()}")
        print(f"   - Reminders: {Reminder.query.count()}")
        print(f"   - Appointments: {Appointment.query.count()}")
        print(f"   - Alerts: {Alert.query.count()}")
        print(f"   - Personal Memories: {PersonalMemory.query.count()}")

if __name__ == '__main__':
    seed_database()
