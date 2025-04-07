from flask import Flask, request, jsonify, send_file, send_from_directory, Response
from flask_cors import CORS
import pandas as pd
import os
import re
import logging
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
app = Flask(__name__, static_folder='static', static_url_path='')

CORS(app)

# === Basic Auth Setup ===
USERNAME = os.environ.get("RENDER_BASIC_AUTH_USER")
PASSWORD = os.environ.get("RENDER_BASIC_AUTH_PASSWORD")

def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    return Response(
        'Access denied.\n', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.before_request
def require_auth_for_all():
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()
# ==========================

# List of negative keywords
negative_keywords = [
    "dimmable"
]

# Compile regex pattern with word boundaries
pattern = re.compile(r'\b(' + '|'.join(map(re.escape, negative_keywords)) + r')\b', re.IGNORECASE)

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        logging.error('No files provided in the request.')
        return jsonify({'error': 'No files provided'}), 400
    files = request.files.getlist('files')
    dataframes = []
    for file in files:
        try:
            df = pd.read_csv(file)
            df['Source File'] = file.filename
            dataframes.append(df)
            logging.info(f"Processed file: {file.filename}")
        except Exception as e:
            logging.exception(f"Error processing file {file.filename}: {str(e)}")
            return jsonify({'error': f"Error processing file {file.filename}: {str(e)}"}), 500
    try:
        combined_df = pd.concat(dataframes, ignore_index=True)
        if 'Keyword Phrase' not in combined_df.columns:
            logging.error("'Keyword Phrase' column not found in the uploaded files.")
            return jsonify({'error': "'Keyword Phrase' column not found in the uploaded files."}), 400
        combined_df.dropna(subset=['Keyword Phrase'], inplace=True)
        mask = ~combined_df['Keyword Phrase'].str.contains(pattern, na=False)
        filtered_df = combined_df[mask]
        filtered_df.drop_duplicates(subset='Keyword Phrase', inplace=True)
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'combined_spreadsheet.xlsx')
        filtered_df.to_excel(output_path, index=False)
        logging.info("Successfully created the combined spreadsheet.")
    except Exception as e:
        logging.exception(f"Error during processing: {str(e)}")
        return jsonify({'error': str(e)}), 500
    try:
        return send_file(output_path, as_attachment=True, download_name='combined_spreadsheet.xlsx')
    except Exception as e:
        logging.exception(f"Error sending file: {str(e)}")
        return jsonify({'error': f"Error sending file: {str(e)}"}), 500

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    if os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        logging.warning(f"Requested path {path} not found. Serving index.html.")
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/get-keywords', methods=['GET'])
def get_keywords():
    return jsonify({'keywords': negative_keywords})

@app.route('/update-keywords', methods=['POST'])
def update_keywords():
    global negative_keywords, pattern
    try:
        data = request.get_json()
        if not data or 'keywords' not in data:
            return jsonify({'error': 'No keywords provided in the request'}), 400
        new_keywords = data['keywords']
        if not isinstance(new_keywords, list) or not all(isinstance(k, str) for k in new_keywords):
            return jsonify({'error': 'Keywords must be a list of strings'}), 400
        negative_keywords = new_keywords
        pattern = re.compile(r'\b(' + '|'.join(map(re.escape, negative_keywords)) + r')\b', re.IGNORECASE)
        logging.info(f"Negative keywords updated: {negative_keywords}")
        return jsonify({'success': True, 'keywords': negative_keywords}), 200
    except Exception as e:
        logging.exception(f"Error updating keywords: {str(e)}")
        return jsonify({'error': f"Error updating keywords: {str(e)}"}), 500

@app.route('/direct-html')
def direct_html():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Keyword Processor</title>
    </head>
    <body>
        <h1>Keyword Processor</h1>
        <p>This page is being served directly by Flask!</p>
        <p>Try to access the <a href="/debug-info">debug info</a> for more details.</p>
    </body>
    </html>
    '''
    return html

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = [
        {
            'id': 1,
            'title': 'Sample Task',
            'description': 'This is a sample task',
            'priority': 'high',
            'dueDate': '2025-04-15',
            'completed': False
        }
    ]
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def create_task():
    task_data = request.get_json()
    if 'title' not in task_data:
        return jsonify({'error': 'Title is required'}), 400
    return jsonify({
        'success': True,
        'message': 'Task created successfully',
        'task': task_data
    }), 201

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    if task_id == 1:
        task = {
            'id': 1,
            'title': 'Sample Task',
            'description': 'This is a sample task',
            'priority': 'high',
            'dueDate': '2025-04-15',
            'completed': False
        }
        return jsonify(task)
    return jsonify({'error': 'Task not found'}), 404

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task_data = request.get_json()
    return jsonify({
        'success': True,
        'message': f'Task {task_id} updated successfully',
        'task': task_data
    })

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    return jsonify({
        'success': True,
        'message': f'Task {task_id} deleted successfully'
    })

@app.errorhandler(404)
def not_found(e):
    logging.warning(f"404 error: {e}. Serving index.html.")
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
