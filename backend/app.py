from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import pandas as pd
import os
import re
import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
app = Flask(__name__, static_folder='static', static_url_path='')

CORS(app)
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
        # Ensure 'Keyword Phrase' column exists
        if 'Keyword Phrase' not in combined_df.columns:
            logging.error("'Keyword Phrase' column not found in the uploaded files.")
            return jsonify({'error': "'Keyword Phrase' column not found in the uploaded files."}), 400
        # Drop rows with NaN in 'Keyword Phrase' to avoid errors
        combined_df.dropna(subset=['Keyword Phrase'], inplace=True)
        # Filter out rows where 'Keyword Phrase' contains any negative keywords with word boundaries
        mask = ~combined_df['Keyword Phrase'].str.contains(pattern, na=False)
        filtered_df = combined_df[mask]
        # Remove duplicates based on 'Keyword Phrase' after filtering
        filtered_df.drop_duplicates(subset='Keyword Phrase', inplace=True)
        # Output directory
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
# Serve React App
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
    
# Load Current Keywords
@app.route('/get-keywords', methods=['GET'])
def get_keywords():
    return jsonify({'keywords': negative_keywords})


@app.route('/update-keywords', methods=['POST'])
def update_keywords():
    global negative_keywords, pattern
    
    try:
        # Get the new keywords from the request
        data = request.get_json()
        if not data or 'keywords' not in data:
            return jsonify({'error': 'No keywords provided in the request'}), 400
        
        new_keywords = data['keywords']
        
        # Validate that keywords is a list of strings
        if not isinstance(new_keywords, list) or not all(isinstance(k, str) for k in new_keywords):
            return jsonify({'error': 'Keywords must be a list of strings'}), 400
        
        # Update the keywords list
        negative_keywords = new_keywords
        
        # Update the regex pattern
        pattern = re.compile(r'\b(' + '|'.join(map(re.escape, negative_keywords)) + r')\b', re.IGNORECASE)
        
        logging.info(f"Negative keywords updated: {negative_keywords}")
        return jsonify({'success': True, 'keywords': negative_keywords}), 200
    
    except Exception as e:
        logging.exception(f"Error updating keywords: {str(e)}")
        return jsonify({'error': f"Error updating keywords: {str(e)}"}), 500



# Add this to your backend/app.py file to help debug
@app.route('/debug-info')
def debug_info():
    """Return debugging information about paths and static files."""
    import os
    
    # Get current directory
    current_dir = os.getcwd()
    
    # Check static folder path
    static_path = os.path.join(current_dir, app.static_folder) if app.static_folder else "No static folder"
    static_exists = os.path.exists(static_path) if app.static_folder else False
    
    # Check if index.html exists
    index_path = os.path.join(static_path, 'index.html') if app.static_folder else "No static folder"
    index_exists = os.path.exists(index_path) if app.static_folder else False
    
    # List files in static folder if it exists
    static_files = os.listdir(static_path) if static_exists else []
    
    debug_data = {
        'current_directory': current_dir,
        'static_folder_setting': app.static_folder,
        'static_url_path_setting': app.static_url_path,
        'full_static_path': static_path,
        'static_folder_exists': static_exists,
        'index_path': index_path,
        'index_html_exists': index_exists,
        'static_files': static_files
    }
    
    return jsonify(debug_data)



@app.route('/direct-html')
def direct_html():
    """Return a simple HTML page directly from the Flask app."""
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




# Error handling for 404 errors
@app.errorhandler(404)
def not_found(e):
    logging.warning(f"404 error: {e}. Serving index.html.")
    return send_from_directory(app.static_folder, 'index.html')
if __name__ == '__main__':
    # Run the app on all interfaces and port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)