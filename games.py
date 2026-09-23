from datetime import datetime
from flask import Blueprint, render_template, request, session, jsonify
from models import db
from models.user import User
from models.patient import Patient
from models.game import Game, GameResult
from models.memory import PersonalMemory
from ai.adaptive_engine import get_ai_engine, calculate_next_difficulty
from . import login_required

games_bp = Blueprint('games', __name__)

def get_current_patient_id():
    pid = session.get('patient_id')
    if pid:
        return pid
    uid = session.get('user_id')
    if uid:
        user = User.query.get(uid)
        if user and user.patient_profile:
            return user.patient_profile.id
    # Fallback to first patient in demo
    first_p = Patient.query.first()
    return first_p.id if first_p else 1

@games_bp.route('/games')
@login_required()
def games_hub_page():
    games = Game.query.all()
    pid = get_current_patient_id()
    # Find patient's current difficulty recommendations
    engine = get_ai_engine()
    recent_results = GameResult.query.filter_by(patient_id=pid).order_by(GameResult.played_at.desc()).limit(5).all()
    recent_dict_list = [r.to_dict() for r in recent_results]
    ai_eval = engine.evaluate(recent_dict_list)

    return render_template(
        'games.html',
        games=games,
        ai_recommendation=ai_eval
    )

@games_bp.route('/games/<slug>')
@login_required()
def play_game_page(slug):
    game = Game.query.filter_by(slug=slug).first_or_404()
    pid = get_current_patient_id()
    recent_results = GameResult.query.filter_by(patient_id=pid, game_id=game.id).order_by(GameResult.played_at.desc()).limit(3).all()
    engine = get_ai_engine()
    eval_res = engine.evaluate([r.to_dict() for r in recent_results])

    template_map = {
        'memory-cards': 'memory_game.html',
        'object-recall': 'object_recall_game.html',
        'pattern-recognition': 'pattern_game.html',
        'attention-game': 'attention_game.html',
        'routine-recall': 'routine_game.html',
        'picture-recognition': 'picture_game.html',
        'emotion-recognition': 'emotion_game.html',
        'family-recall': 'family_recall_game.html'
    }
    target_template = template_map.get(slug, 'memory_game.html')

    return render_template(
        target_template,
        game=game,
        initial_difficulty=eval_res.get('difficulty', game.difficulty),
        ai_eval=eval_res
    )

# REST API Endpoints
@games_bp.route('/api/games', methods=['GET'])
def api_games_list():
    games = Game.query.all()
    return jsonify([g.to_dict() for g in games]), 200

@games_bp.route('/api/games/result', methods=['POST'])
@login_required()
def api_record_game_result():
    data = request.get_json() or {}
    patient_id = data.get('patient_id') or get_current_patient_id()
    game_slug = data.get('game_slug')
    game_id = data.get('game_id')
    score = int(data.get('score', 0))
    accuracy = float(data.get('accuracy', 100.0))
    completion_time = float(data.get('completion_time', 0.0))
    attempts = int(data.get('attempts', 1))
    current_difficulty = data.get('difficulty', 'EASY')

    if not game_id and game_slug:
        game = Game.query.filter_by(slug=game_slug).first()
        if game:
            game_id = game.id
        else:
            game_id = 1
    elif not game_id:
        game_id = 1

    try:
        result = GameResult(
            patient_id=patient_id,
            game_id=game_id,
            score=score,
            accuracy=accuracy,
            completion_time=completion_time,
            attempts=attempts,
            difficulty=current_difficulty,
            played_at=datetime.now()
        )
        db.session.add(result)
        db.session.commit()

        # Run AI Adaptive difficulty engine
        engine = get_ai_engine()
        history = GameResult.query.filter_by(patient_id=patient_id).order_by(GameResult.played_at.desc()).limit(5).all()
        ai_feedback = engine.evaluate([r.to_dict() for r in history])

        return jsonify({
            'message': 'Game result recorded successfully',
            'result': result.to_dict(),
            'ai_difficulty': ai_feedback['difficulty'],
            'ai_feedback': ai_feedback
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@games_bp.route('/api/games/history', methods=['GET'])
@login_required()
def api_games_history():
    patient_id = request.args.get('patient_id', type=int) or get_current_patient_id()
    results = GameResult.query.filter_by(patient_id=patient_id).order_by(GameResult.played_at.desc()).limit(20).all()
    return jsonify([r.to_dict() for r in results]), 200

@games_bp.route('/api/ai/difficulty', methods=['POST'])
def api_ai_difficulty():
    data = request.get_json() or {}
    engine = get_ai_engine()
    feedback = engine.evaluate(data)
    return jsonify(feedback), 200

@games_bp.route('/api/games/personal-questions', methods=['GET'])
@login_required()
def api_personal_questions():
    import random
    pid = get_current_patient_id()
    memories = PersonalMemory.query.filter_by(patient_id=pid).all()

    family_distractors = ["Sunita Sharma (Daughter)", "Aarav Kumar (Grandson)", "Hemlata Devi (Wife)", "Ramesh Chandra (Son)", "Meera Baruah (Sister)", "Priya Devi (Niece)"]
    show_distractors = ["Ramayan (DD National)", "Mahabharat", "Shaktimaan", "Zubeen Garg Folk Melodies", "Bihu Geet Classics", "DD News"]
    address_distractors = ["House #14, Zoo Road, Guwahati", "Station Road, Dispur", "GS Road, Shillong", "Civil Lines, Tezpur", "MG Road, Jorhat"]

    questions = []

    for m in memories:
        if m.category == 'family':
            correct = f"{m.title} ({m.relationship_or_type})"
            opts = [correct]
            for d in family_distractors:
                if d != correct and d not in opts and len(opts) < 4:
                    opts.append(d)
            random.shuffle(opts)
            questions.append({
                'category': 'Family Member',
                'question': f"Who is this loving person in your family?",
                'clue': m.details or f"Your loving {m.relationship_or_type}",
                'image_url': m.image_url,
                'icon': 'fa-user-heart',
                'correct': correct,
                'options': opts
            })
        elif m.category == 'favorite_show':
            correct = m.title
            opts = [correct]
            for d in show_distractors:
                if d != correct and d not in opts and len(opts) < 4:
                    opts.append(d)
            random.shuffle(opts)
            questions.append({
                'category': 'Favorite Show & Music',
                'question': f"Which television show or song do you love to watch?",
                'clue': m.details or f"Watched together with your family",
                'image_url': m.image_url,
                'icon': 'fa-tv',
                'correct': correct,
                'options': opts
            })
        elif m.category == 'address':
            correct = m.title
            opts = [correct]
            for d in address_distractors:
                if d != correct and d not in opts and len(opts) < 4:
                    opts.append(d)
            random.shuffle(opts)
            questions.append({
                'category': 'Familiar Address & Home',
                'question': f"What is your familiar {m.relationship_or_type}?",
                'clue': m.details or f"Your home in North-East India",
                'image_url': m.image_url,
                'icon': 'fa-house',
                'correct': correct,
                'options': opts
            })

    # If few memories, provide gentle realistic default questions
    if len(questions) < 3:
        defaults = [
            {
                'category': 'Family Member',
                'question': "Who is your primary family caregiver and loving daughter?",
                'clue': "Visits you every Sunday with homemade warm pitha.",
                'image_url': 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=300&auto=format&fit=crop&q=80',
                'icon': 'fa-user-heart',
                'correct': 'Sunita Sharma (Daughter)',
                'options': ['Sunita Sharma (Daughter)', 'Priya Devi (Niece)', 'Kavita Baruah (Neighbor)', 'Meera (Sister)']
            },
            {
                'category': 'Favorite Show',
                'question': "Which legendary serial do you love to watch in the evening?",
                'clue': "Broadcasted on DD National, tells the epic story of Rama.",
                'image_url': 'https://images.unsplash.com/photo-1522869635100-9f4c5e86aa37?w=300&auto=format&fit=crop&q=80',
                'icon': 'fa-tv',
                'correct': 'Ramayan (DD National)',
                'options': ['Ramayan (DD National)', 'Cricket Match', 'Morning News', 'Crime Patrol']
            },
            {
                'category': 'Home Address',
                'question': "Where is your familiar home located in Assam?",
                'clue': "House #14 near the peaceful greenery of Zoo Road, Guwahati.",
                'image_url': 'https://images.unsplash.com/photo-1518780664697-55e3ad937233?w=300&auto=format&fit=crop&q=80',
                'icon': 'fa-house',
                'correct': 'House #14, Zoo Road, Guwahati',
                'options': ['House #14, Zoo Road, Guwahati', 'Station Road, Dispur', 'GS Road, Shillong', 'Civil Lines, Tezpur']
            }
        ]
        for d in defaults:
            if not any(q['correct'] == d['correct'] for q in questions):
                questions.append(d)

    return jsonify({'success': True, 'questions': questions}), 200

