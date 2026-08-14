from flask import Flask, jsonify, request, send_from_directory, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from pathlib import Path
from uuid import uuid4
from datetime import datetime
import json
import os
import re

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
UPLOAD_DIR = BASE_DIR / 'uploads'

DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'
SECRET_KEY = os.environ.get('IMLEM_SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'dev-only-change-in-production'
    else:
        raise RuntimeError(
            'IMLEM_SECRET_KEY environment variable is required when FLASK_DEBUG is not set to 1. '
            'Generate one with: python -c "import secrets; print(secrets.token_hex(32))"'
        )

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.secret_key = SECRET_KEY
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = not DEBUG

DIVISION_NAMES = [
    'Euclid', 'Pythagoras', 'Pascal', 'Fibonacci', 'da Vinci',
    'Martinoli', 'Quaden', 'Mosca', 'Gauss', 'Hypatia', 'Ramanujan', 'Lexington',
]

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
MAX_NAME_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 1000
MIN_PASSWORD_LENGTH = 8


def _validate_name(name, field='name'):
    if not name or not name.strip():
        return f'{field} is required'
    if len(name) > MAX_NAME_LENGTH:
        return f'{field} must be {MAX_NAME_LENGTH} characters or fewer'
    return None


def _validate_description(description):
    if description and len(description) > MAX_DESCRIPTION_LENGTH:
        return f'description must be {MAX_DESCRIPTION_LENGTH} characters or fewer'
    return None


def _validate_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except (TypeError, ValueError):
        return 'date must be in YYYY-MM-DD format'
    return None

DEFAULTS = {
    'study-materials.json': {'years': []},
    'meets.json': {'records': []},
    'divisions.json': {'records': [
        {'id': f'div-{name.lower().replace(" ", "-")}', 'name': name, 'teams': []}
        for name in DIVISION_NAMES
    ]},
    'statistics.json': {'records': []},
    'users.json': {'accounts': [
        {
            'id': 'admin-1',
            'name': 'Site Administrator',
            'role': 'admin',
            'divisionId': None,
            'schoolId': None,
            'email': 'admin@imlem.org',
            'passwordHash': generate_password_hash('admin123'),
        },
        {
            'id': 'coach-1',
            'name': 'Sample Elementary Coach',
            'role': 'coach',
            'divisionId': 'div-euclid',
            'schoolId': 'school-1',
            'email': 'coach@imlem.org',
            'passwordHash': generate_password_hash('coach123'),
        },
    ]},
}


def ensure_json(filename):
    path = DATA_DIR / filename
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps(DEFAULTS.get(filename, {}), indent=2), encoding='utf-8')
    return path


def read_json(filename):
    path = ensure_json(filename)
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(filename, data):
    path = ensure_json(filename)
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')


def current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    users = read_json('users.json')
    return next((u for u in users['accounts'] if u['id'] == user_id), None)


def _public_user(user):
    return {
        'id': user['id'],
        'name': user['name'],
        'role': user['role'],
        'email': user['email'],
        'divisionId': user.get('divisionId'),
        'schoolId': user.get('schoolId'),
    }


def require_role(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            user = current_user()
            if not user:
                return jsonify({'error': 'Authentication required'}), 401
            if user['role'] not in allowed_roles:
                return jsonify({'error': 'Forbidden'}), 403
            request.current_user = user
            return view_func(*args, **kwargs)
        return wrapped
    return decorator


@app.route('/api/login', methods=['POST'])
def login():
    payload = request.get_json() or {}
    email = (payload.get('email') or '').strip().lower()
    password = payload.get('password') or ''
    users = read_json('users.json')
    user = next((u for u in users['accounts'] if u['email'].lower() == email), None)
    if not user or not check_password_hash(user.get('passwordHash', ''), password):
        return jsonify({'error': 'Invalid email or password'}), 401
    session['user_id'] = user['id']
    return jsonify(_public_user(user))


@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'success': True})


@app.route('/api/me', methods=['GET'])
def me():
    user = current_user()
    if not user:
        return jsonify({'user': None})
    return jsonify({'user': _public_user(user)})


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)


@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(BASE_DIR / 'images', filename)


@app.route('/api/study-materials', methods=['GET'])
def get_study_materials():
    return jsonify(read_json('study-materials.json'))


@app.route('/api/meets', methods=['GET'])
def get_meets():
    return jsonify(read_json('meets.json'))


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    return jsonify(read_json('statistics.json'))


@app.route('/api/divisions', methods=['GET'])
def get_divisions():
    return jsonify(read_json('divisions.json'))


@app.route('/api/divisions', methods=['POST'])
@require_role('admin')
def create_division():
    payload = request.get_json() or {}
    name = payload.get('name')
    error = _validate_name(name, 'name')
    if error:
        return jsonify({'error': error}), 400

    store = read_json('divisions.json')
    record = {'id': str(uuid4()), 'name': name, 'teams': []}
    store['records'].append(record)
    write_json('divisions.json', store)
    return jsonify(record)


@app.route('/api/divisions/<division_id>', methods=['DELETE'])
@require_role('admin')
def delete_division(division_id):
    store = read_json('divisions.json')
    division = next((d for d in store['records'] if d['id'] == division_id), None)
    if not division:
        return jsonify({'error': 'Division not found'}), 404

    school_ids = {t['id'] for t in division['teams']}
    users = read_json('users.json')
    dependent_count = sum(
        1 for u in users['accounts']
        if u.get('divisionId') == division_id and u.get('schoolId') in school_ids
    )
    if dependent_count:
        return jsonify({
            'error': f'{dependent_count} coach account(s) are tied to schools in this division. '
                     'Delete those coach accounts first.'
        }), 400

    store['records'] = [d for d in store['records'] if d['id'] != division_id]
    write_json('divisions.json', store)
    return jsonify({'success': True})


@app.route('/api/divisions/<division_id>/teams', methods=['POST'])
@require_role('admin')
def add_division_team(division_id):
    payload = request.get_json() or {}
    name = payload.get('name')
    description = payload.get('description', '')
    error = _validate_name(name, 'name') or _validate_description(description)
    if error:
        return jsonify({'error': error}), 400

    store = read_json('divisions.json')
    division = next((entry for entry in store['records'] if entry['id'] == division_id), None)
    if not division:
        return jsonify({'error': 'Division not found'}), 404

    team = {
        'id': str(uuid4()),
        'name': name,
        'description': description,
        'roster': [],
        'scores': [None, None, None, None, None],
    }
    division['teams'].append(team)
    write_json('divisions.json', store)
    return jsonify(team)


@app.route('/api/divisions/<division_id>/teams/<team_id>/info', methods=['PUT'])
@require_role('admin')
def update_division_team_info(division_id, team_id):
    payload = request.get_json() or {}
    if 'name' in payload:
        error = _validate_name(payload['name'], 'name')
        if error:
            return jsonify({'error': error}), 400
    if 'description' in payload:
        error = _validate_description(payload['description'])
        if error:
            return jsonify({'error': error}), 400

    store = read_json('divisions.json')
    division = next((entry for entry in store['records'] if entry['id'] == division_id), None)
    if not division:
        return jsonify({'error': 'Division not found'}), 404

    team = next((entry for entry in division['teams'] if entry['id'] == team_id), None)
    if not team:
        return jsonify({'error': 'Team not found'}), 404

    team['name'] = payload.get('name', team['name'])
    team['description'] = payload.get('description', team.get('description', ''))
    write_json('divisions.json', store)
    return jsonify(team)


@app.route('/api/divisions/<division_id>/teams/<team_id>', methods=['PUT'])
@require_role('admin')
def update_division_team_score(division_id, team_id):
    payload = request.get_json() or {}
    meet_number = payload.get('meetNumber')
    score = payload.get('score')
    if meet_number is None or score is None:
        return jsonify({'error': 'meetNumber and score are required'}), 400

    try:
        meet_index = int(meet_number) - 1
    except (TypeError, ValueError):
        return jsonify({'error': 'meetNumber must be a number between 1 and 5'}), 400
    if meet_index < 0 or meet_index > 4:
        return jsonify({'error': 'meetNumber must be between 1 and 5'}), 400

    store = read_json('divisions.json')
    division = next((entry for entry in store['records'] if entry['id'] == division_id), None)
    if not division:
        return jsonify({'error': 'Division not found'}), 404

    team = next((entry for entry in division['teams'] if entry['id'] == team_id), None)
    if not team:
        return jsonify({'error': 'Team not found'}), 404

    team['scores'][meet_index] = score
    write_json('divisions.json', store)
    return jsonify(team)


@app.route('/api/divisions/<division_id>/teams/<team_id>', methods=['DELETE'])
@require_role('admin')
def delete_division_team(division_id, team_id):
    store = read_json('divisions.json')
    division = next((entry for entry in store['records'] if entry['id'] == division_id), None)
    if not division:
        return jsonify({'error': 'Division not found'}), 404

    if not any(t['id'] == team_id for t in division['teams']):
        return jsonify({'error': 'Team not found'}), 404

    users = read_json('users.json')
    dependent_count = sum(
        1 for u in users['accounts']
        if u.get('divisionId') == division_id and u.get('schoolId') == team_id
    )
    if dependent_count:
        return jsonify({
            'error': f'{dependent_count} coach account(s) are tied to this school. '
                     'Delete those coach accounts first.'
        }), 400

    division['teams'] = [t for t in division['teams'] if t['id'] != team_id]
    write_json('divisions.json', store)
    return jsonify({'success': True})


@app.route('/api/my-school', methods=['GET'])
@require_role('coach')
def get_my_school():
    user = request.current_user
    divisions = read_json('divisions.json')
    division = next((d for d in divisions['records'] if d['id'] == user.get('divisionId')), None)
    if not division:
        return jsonify({'error': 'Division not found'}), 404
    team = next((t for t in division['teams'] if t['id'] == user.get('schoolId')), None)
    if not team:
        return jsonify({'error': 'School not found'}), 404
    return jsonify({'division': {'id': division['id'], 'name': division['name']}, 'school': team})


@app.route('/api/my-school', methods=['PUT'])
@require_role('coach')
def update_my_school():
    payload = request.get_json() or {}
    if 'name' in payload:
        error = _validate_name(payload['name'], 'name')
        if error:
            return jsonify({'error': error}), 400
    if 'description' in payload:
        error = _validate_description(payload['description'])
        if error:
            return jsonify({'error': error}), 400

    user = request.current_user
    divisions = read_json('divisions.json')
    division = next((d for d in divisions['records'] if d['id'] == user.get('divisionId')), None)
    if not division:
        return jsonify({'error': 'Division not found'}), 404
    team = next((t for t in division['teams'] if t['id'] == user.get('schoolId')), None)
    if not team:
        return jsonify({'error': 'School not found'}), 404

    if 'name' in payload:
        team['name'] = payload['name']
    if 'description' in payload:
        team['description'] = payload['description']
    if 'roster' in payload:
        team['roster'] = payload['roster']
    write_json('divisions.json', divisions)
    return jsonify(team)


@app.route('/api/users', methods=['GET'])
@require_role('admin')
def get_users():
    store = read_json('users.json')
    return jsonify({'accounts': [_public_user(u) for u in store['accounts']]})


@app.route('/api/users', methods=['POST'])
@require_role('admin')
def create_user():
    payload = request.get_json() or {}
    name = payload.get('name')
    email = (payload.get('email') or '').strip().lower()
    password = payload.get('password')
    division_id = payload.get('divisionId')
    school_id = payload.get('schoolId')
    if not name or not email or not password or not division_id or not school_id:
        return jsonify({'error': 'name, email, password, divisionId and schoolId are required'}), 400

    name_error = _validate_name(name, 'name')
    if name_error:
        return jsonify({'error': name_error}), 400
    if not EMAIL_RE.match(email):
        return jsonify({'error': 'email is not a valid email address'}), 400
    if len(password) < MIN_PASSWORD_LENGTH:
        return jsonify({'error': f'password must be at least {MIN_PASSWORD_LENGTH} characters'}), 400

    divisions = read_json('divisions.json')
    division = next((d for d in divisions['records'] if d['id'] == division_id), None)
    if not division or not any(t['id'] == school_id for t in division['teams']):
        return jsonify({'error': 'School not found in the given division'}), 404

    store = read_json('users.json')
    if any(u['email'].lower() == email for u in store['accounts']):
        return jsonify({'error': 'An account with that email already exists'}), 400

    user = {
        'id': str(uuid4()),
        'name': name,
        'role': 'coach',
        'divisionId': division_id,
        'schoolId': school_id,
        'email': email,
        'passwordHash': generate_password_hash(password),
    }
    store['accounts'].append(user)
    write_json('users.json', store)
    return jsonify(_public_user(user))


@app.route('/api/users/<user_id>', methods=['DELETE'])
@require_role('admin')
def delete_user(user_id):
    current = request.current_user
    if current['id'] == user_id:
        return jsonify({'error': 'You cannot delete your own account while logged in'}), 400

    store = read_json('users.json')
    target = next((u for u in store['accounts'] if u['id'] == user_id), None)
    if not target:
        return jsonify({'error': 'Account not found'}), 404

    if target['role'] == 'admin':
        admin_count = sum(1 for u in store['accounts'] if u['role'] == 'admin')
        if admin_count <= 1:
            return jsonify({'error': 'Cannot delete the last remaining admin account'}), 400

    store['accounts'] = [u for u in store['accounts'] if u['id'] != user_id]
    write_json('users.json', store)
    return jsonify({'success': True})


@app.route('/api/me/password', methods=['PUT'])
@require_role('admin', 'coach')
def change_my_password():
    payload = request.get_json() or {}
    current_password = payload.get('currentPassword') or ''
    new_password = payload.get('newPassword') or ''

    user = request.current_user
    if not check_password_hash(user.get('passwordHash', ''), current_password):
        return jsonify({'error': 'Current password is incorrect'}), 401
    if len(new_password) < MIN_PASSWORD_LENGTH:
        return jsonify({'error': f'New password must be at least {MIN_PASSWORD_LENGTH} characters'}), 400

    store = read_json('users.json')
    target = next((u for u in store['accounts'] if u['id'] == user['id']), None)
    if not target:
        return jsonify({'error': 'Account not found'}), 404

    target['passwordHash'] = generate_password_hash(new_password)
    write_json('users.json', store)
    return jsonify({'success': True})


@app.route('/api/upload-file', methods=['POST'])
@require_role('admin')
def upload_file():
    year = request.form.get('year')
    meet_number = request.form.get('meetNumber')
    file_type = request.form.get('type')
    uploaded_file = request.files.get('file')

    if not year or not meet_number or not file_type or not uploaded_file:
        return jsonify({'error': 'year, meetNumber, type and file are required'}), 400

    if uploaded_file.content_type != 'application/pdf':
        return jsonify({'error': 'Only PDF files are accepted'}), 400

    target_dir = UPLOAD_DIR / str(year) / str(meet_number) / file_type
    target_dir.mkdir(parents=True, exist_ok=True)

    safe_name = ''.join(c if c.isalnum() or c in '._-' else '_' for c in uploaded_file.filename)
    filename = f"{int(datetime.utcnow().timestamp())}_{safe_name}"
    destination = target_dir / filename
    uploaded_file.save(destination)

    archive = read_json('study-materials.json')
    year_key = str(year)
    year_entry = next((entry for entry in archive['years'] if entry['year'] == year_key), None)
    if not year_entry:
        year_entry = {'year': year_key, 'meets': []}
        archive['years'].append(year_entry)

    meet_entry = next((entry for entry in year_entry['meets'] if entry['meetNumber'] == str(meet_number)), None)
    if not meet_entry:
        meet_entry = {'meetNumber': str(meet_number), 'files': []}
        year_entry['meets'].append(meet_entry)

    file_entry = {
        'id': str(uuid4()),
        'type': file_type,
        'title': request.form.get('title') or uploaded_file.filename,
        'filename': filename,
        'originalName': uploaded_file.filename,
        'url': f"/uploads/{year_key}/{meet_number}/{file_type}/{filename}",
        'uploadedAt': datetime.utcnow().isoformat() + 'Z'
    }
    meet_entry['files'].append(file_entry)
    write_json('study-materials.json', archive)
    return jsonify({'success': True, 'file': file_entry})


@app.route('/api/meets', methods=['POST'])
@require_role('admin')
def create_meet():
    payload = request.get_json() or {}
    if not payload.get('date'):
        return jsonify({'error': 'date is required'}), 400
    date_error = _validate_date(payload['date'])
    if date_error:
        return jsonify({'error': date_error}), 400
    description_error = _validate_description(payload.get('location', '')) or _validate_description(payload.get('announcement', ''))
    if description_error:
        return jsonify({'error': description_error}), 400

    store = read_json('meets.json')
    record = {
        'id': str(uuid4()),
        'date': payload['date'],
        'time': payload.get('time', ''),
        'location': payload.get('location', ''),
        'announcement': payload.get('announcement', ''),
        'createdAt': '',
    }
    store['records'].append(record)
    write_json('meets.json', store)
    return jsonify(record)


@app.route('/api/meets/<meet_id>', methods=['PUT'])
@require_role('admin')
def update_meet(meet_id):
    updates = request.get_json() or {}
    if 'date' in updates:
        date_error = _validate_date(updates['date'])
        if date_error:
            return jsonify({'error': date_error}), 400

    store = read_json('meets.json')
    record = next((entry for entry in store['records'] if entry['id'] == meet_id), None)
    if not record:
        return jsonify({'error': 'Meet not found'}), 404

    record['location'] = updates.get('location', record['location'])
    record['date'] = updates.get('date', record['date'])
    record['time'] = updates.get('time', record['time'])
    record['announcement'] = updates.get('announcement', record['announcement'])
    write_json('meets.json', store)
    return jsonify(record)


@app.route('/api/meets/<meet_id>', methods=['DELETE'])
@require_role('admin')
def delete_meet(meet_id):
    store = read_json('meets.json')
    remaining = [m for m in store['records'] if m['id'] != meet_id]
    if len(remaining) == len(store['records']):
        return jsonify({'error': 'Meet not found'}), 404

    store['records'] = remaining
    write_json('meets.json', store)
    return jsonify({'success': True})


if __name__ == '__main__':
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    for name in DEFAULTS:
        ensure_json(name)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=DEBUG)
