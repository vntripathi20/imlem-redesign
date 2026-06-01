from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
from pathlib import Path
from uuid import uuid4
from datetime import datetime
import json

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
UPLOAD_DIR = BASE_DIR / 'uploads'

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

DEFAULTS = {
    'study-materials.json': {'years': []},
    'meets.json': {'records': []},
    'clusters.json': {'records': [
        {
            'id': 'cluster-1',
            'name': 'North Shore Cluster',
            'coordinator': 'Coordinator A',
            'location': 'Region A',
            'announcement': '',
            'updatedAt': None,
        }
    ]},
    'statistics.json': {'records': []},
    'users.json': {'accounts': [
        {
            'id': 'admin-1',
            'name': 'Site Administrator',
            'role': 'admin',
            'clusterId': None,
            'email': 'admin@imlem.org',
        },
        {
            'id': 'coord-1',
            'name': 'Cluster Coordinator',
            'role': 'coordinator',
            'clusterId': 'cluster-1',
            'email': 'coord@imlem.org',
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


@app.route('/api/clusters', methods=['GET'])
def get_clusters():
    return jsonify(read_json('clusters.json'))


@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    return jsonify(read_json('statistics.json'))


@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(read_json('users.json'))


@app.route('/api/upload-file', methods=['POST'])
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
def create_meet():
    payload = request.get_json() or {}
    if not payload.get('clusterId') or not payload.get('date'):
        return jsonify({'error': 'clusterId and date are required'}), 400

    store = read_json('meets.json')
    record = {
        'id': str(uuid4()),
        'clusterId': payload['clusterId'],
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
def update_meet(meet_id):
    updates = request.get_json() or {}
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


@app.route('/api/announcements', methods=['POST'])
def post_announcements():
    payload = request.get_json() or {}
    cluster_id = payload.get('clusterId')
    message = payload.get('message')
    if not cluster_id or not message:
        return jsonify({'error': 'clusterId and message are required'}), 400

    store = read_json('clusters.json')
    cluster = next((entry for entry in store['records'] if entry['id'] == cluster_id), None)
    if not cluster:
        return jsonify({'error': 'Cluster not found'}), 404

    cluster['announcement'] = message
    cluster['updatedAt'] = ''
    write_json('clusters.json', store)
    return jsonify(cluster)


if __name__ == '__main__':
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    for name in DEFAULTS:
        ensure_json(name)
    app.run(host='0.0.0.0', port=5000, debug=True)
