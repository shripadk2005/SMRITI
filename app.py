import os
from flask import Flask, render_template, session, jsonify
from config import Config
from models import db
from models.user import User
from models.patient import Patient
from models.caregiver import Caregiver
from models.game import Game

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.patient import patient_bp
    from routes.caregiver import caregiver_bp
    from routes.games import games_bp
    from routes.reminders import reminders_bp
    from routes.appointments import appointments_bp
    from routes.analytics import analytics_bp
    from routes.sync import sync_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(caregiver_bp)
    app.register_blueprint(games_bp)
    app.register_blueprint(reminders_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(sync_bp)

    # Global Context Processor
    @app.context_processor
    def inject_global_vars():
        current_user = None
        user_role = session.get('user_role')
        patient_obj = None
        if 'user_id' in session:
            current_user = User.query.get(session['user_id'])
            if current_user and current_user.patient_profile:
                patient_obj = current_user.patient_profile
        
        return {
            'logged_user': current_user,
            'user_role': user_role,
            'current_patient': patient_obj,
            'active_language': session.get('user_lang', 'en')
        }

    # Public Landing Page
    @app.route('/')
    def public_index():
        return render_template('index.html')

    @app.route('/service-worker.js')
    def service_worker():
        return app.send_static_file('service-worker.js')

    @app.route('/manifest.json')
    def manifest():
        return app.send_static_file('manifest.json')

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    # Auto-initialize database tables within app context
    with app.app_context():
        db.create_all()
        # Seed default games if not present
        if Game.query.count() == 0:
            default_games = [
                Game(
                    slug='memory-cards',
                    name='Memory Cards',
                    category='Memory',
                    difficulty='EASY',
                    description='Match pairs of familiar North-Eastern cultural symbols (Tea Cup, Japi, Rice Bowl, Hornbill).',
                    icon='fa-clone'
                ),
                Game(
                    slug='object-recall',
                    name='Remember the Objects',
                    category='Memory',
                    difficulty='EASY',
                    description='Memorize 6 household and cultural objects for 10 seconds, then recall them.',
                    icon='fa-eye'
                ),
                Game(
                    slug='pattern-recognition',
                    name='Pattern Recognition',
                    category='Pattern',
                    difficulty='MEDIUM',
                    description='Identify the next logical shape or color in a sequence.',
                    icon='fa-shapes'
                ),
                Game(
                    slug='attention-game',
                    name='Focus & Attention',
                    category='Attention',
                    difficulty='EASY',
                    description='Find the target object among visual distractors as quickly and accurately as possible.',
                    icon='fa-bullseye'
                ),
                Game(
                    slug='routine-recall',
                    name='Daily Routine Recall',
                    category='Daily Routine',
                    difficulty='EASY',
                    description='Recall your sequential morning, afternoon, and evening activities in order.',
                    icon='fa-calendar-check'
                ),
                Game(
                    slug='picture-recognition',
                    name='Familiar Picture Recognition',
                    category='Recognition',
                    difficulty='EASY',
                    description='Recognize familiar NER heritage items, tea gardens, and traditional musical instruments.',
                    icon='fa-image'
                ),
                Game(
                    slug='emotion-recognition',
                    name='Emotional Perception',
                    category='Emotional Recognition',
                    difficulty='EASY',
                    description='Look at friendly expressions and choose how the person feels in a calming environment.',
                    icon='fa-smile'
                )
            ]
            db.session.bulk_save_objects(default_games)
            db.session.commit()

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 MindCare NER server running at http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
