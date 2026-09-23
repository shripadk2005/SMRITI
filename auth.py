from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import db
from models.user import User
from models.patient import Patient
from models.caregiver import Caregiver

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'GET':
        if 'user_id' in session:
            role = session.get('user_role')
            if role == 'caregiver':
                return redirect(url_for('caregiver.dashboard_page'))
            elif role == 'admin':
                return redirect(url_for('analytics.admin_dashboard_page'))
            return redirect(url_for('patient.dashboard_page'))
        return render_template('login.html')
    
    # Process form POST
    email_or_phone = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    requested_role = request.form.get('role', '')

    if not email_or_phone or not password:
        flash('Please provide both your email/phone and password.', 'danger')
        return render_template('login.html', email=email_or_phone)

    user = User.query.filter(
        (User.email == email_or_phone) | (User.phone == email_or_phone)
    ).first()

    if not user or not user.check_password(password):
        flash('Invalid email/phone or password. Please try again.', 'danger')
        return render_template('login.html', email=email_or_phone)

    if requested_role and requested_role != user.role:
        flash(f'Account exists, but registered role is "{user.role.title()}".', 'warning')

    # Establish session
    session.permanent = True
    session['user_id'] = user.id
    session['user_name'] = user.name
    session['user_role'] = user.role
    session['user_email'] = user.email
    session['user_lang'] = user.language or 'en'

    if user.role == 'patient' and user.patient_profile:
        session['patient_id'] = user.patient_profile.id
    elif user.role == 'caregiver' and user.caregiver_profile:
        session['caregiver_id'] = user.caregiver_profile.id

    flash(f'Welcome back, {user.name}!', 'success')
    next_url = request.args.get('next')
    if next_url and next_url.startswith('/'):
        return redirect(next_url)

    if user.role == 'caregiver':
        return redirect(url_for('caregiver.dashboard_page'))
    elif user.role == 'admin':
        return redirect(url_for('analytics.admin_dashboard_page'))
    return redirect(url_for('patient.dashboard_page'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'GET':
        return render_template('register.html')

    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip().lower()
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '')
    role = request.form.get('role', 'patient').strip().lower()
    age = request.form.get('age')
    gender = request.form.get('gender', 'Other')
    language = request.form.get('language', 'en')
    emergency_contact = request.form.get('emergency_contact', '').strip()
    region = request.form.get('region', 'Assam').strip()

    if not name or not email or not password:
        flash('Name, email, and password are required.', 'danger')
        return render_template('register.html')

    if User.query.filter_by(email=email).first():
        flash('An account with this email already exists.', 'warning')
        return render_template('register.html')

    try:
        user = User(
            name=name,
            email=email,
            phone=phone,
            role=role,
            age=int(age) if age and age.isdigit() else None,
            gender=gender,
            language=language
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        if role == 'patient':
            patient = Patient(
                user_id=user.id,
                emergency_contact=emergency_contact or phone,
                region=region
            )
            db.session.add(patient)
            db.session.flush()
            session['patient_id'] = patient.id
        elif role == 'caregiver':
            caregiver = Caregiver(
                user_id=user.id,
                relationship_to_patient='Family Caregiver'
            )
            db.session.add(caregiver)
            db.session.flush()
            session['caregiver_id'] = caregiver.id

        db.session.commit()

        # Log user in
        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_role'] = user.role
        session['user_email'] = user.email
        session['user_lang'] = user.language or 'en'

        flash('Registration successful! Welcome to MindCare NER.', 'success')
        if role == 'caregiver':
            return redirect(url_for('caregiver.dashboard_page'))
        elif role == 'admin':
            return redirect(url_for('analytics.admin_dashboard_page'))
        return redirect(url_for('patient.dashboard_page'))

    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred during registration: {str(e)}', 'danger')
        return render_template('register.html')

@auth_bp.route('/logout')
def logout_page():
    session.clear()
    flash('You have been safely logged out.', 'info')
    return redirect(url_for('public_index'))

@auth_bp.route('/unauthorized')
def unauthorized_page():
    return render_template('404.html', message="You do not have permission to access this page."), 403

# REST API Endpoints
@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    email_or_phone = data.get('email', '').strip()
    password = data.get('password', '')

    if not email_or_phone or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter(
        (User.email == email_or_phone) | (User.phone == email_or_phone)
    ).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401

    session.permanent = True
    session['user_id'] = user.id
    session['user_name'] = user.name
    session['user_role'] = user.role
    session['user_email'] = user.email
    session['user_lang'] = user.language or 'en'

    patient_id = None
    if user.role == 'patient' and user.patient_profile:
        patient_id = user.patient_profile.id
        session['patient_id'] = patient_id
    elif user.role == 'caregiver' and user.caregiver_profile:
        session['caregiver_id'] = user.caregiver_profile.id

    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'patient_id': patient_id
    }), 200

@auth_bp.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    role = data.get('role', 'patient').strip().lower()
    phone = data.get('phone', '').strip()
    age = data.get('age')
    gender = data.get('gender')
    language = data.get('language', 'en')
    emergency_contact = data.get('emergency_contact', '').strip()
    region = data.get('region', 'Assam')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'An account with this email already exists'}), 409

    try:
        user = User(
            name=name,
            email=email,
            phone=phone,
            role=role,
            age=int(age) if age else None,
            gender=gender,
            language=language
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        patient_id = None
        if role == 'patient':
            patient = Patient(
                user_id=user.id,
                emergency_contact=emergency_contact or phone,
                region=region
            )
            db.session.add(patient)
            db.session.flush()
            patient_id = patient.id
            session['patient_id'] = patient.id
        elif role == 'caregiver':
            caregiver = Caregiver(user_id=user.id)
            db.session.add(caregiver)
            db.session.flush()
            session['caregiver_id'] = caregiver.id

        db.session.commit()

        session['user_id'] = user.id
        session['user_name'] = user.name
        session['user_role'] = user.role
        session['user_email'] = user.email
        session['user_lang'] = user.language

        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'patient_id': patient_id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/api/current_user', methods=['GET'])
def api_current_user():
    if 'user_id' not in session:
        return jsonify({'authenticated': False}), 200
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return jsonify({'authenticated': False}), 200
    
    resp = {
        'authenticated': True,
        'user': user.to_dict(),
        'patient_id': session.get('patient_id'),
        'caregiver_id': session.get('caregiver_id')
    }
    return jsonify(resp), 200
