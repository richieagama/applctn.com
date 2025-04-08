from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from playwright.sync_api import sync_playwright

import pandas as pd
import os
import re
import logging
import json


# Configure logging
logging.basicConfig(level=logging.INFO)
app = Flask(__name__, static_folder='static', static_url_path='')

CORS(app)
# List of negative keywords
negative_keywords = [
    "sunco","chandelier","home depot"
]

# List of asins 
asin_list = ["B09D1LMDN2"]

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


# Load Current ASINS
@app.route('/get-asins', methods=['GET'])
def get_asins():
    return jsonify({'asins': asin_list})


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
    

@app.route('/start-cerebro-bot', methods=['POST'])
def process_helium10_asins():
    global asin_list, pattern

    
    with sync_playwright() as p:
        # Launch browser
        #browser = p.chromium.launch(headless=True)


        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--single-process'  # Critical for memory-constrained environments
            ]
        )        
        
        # Create context
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        
        # Load cookies from file 
        #with open("helium10_auth_cookies.json", "r") as f:
        #    cookies = json.load(f)
        #context.add_cookies(cookies)


        # Load cookies from environment variable
        try:
            cookies_json = os.environ.get("HELIUM10_COOKIES")
            if not cookies_json:
                raise Exception("HELIUM10_COOKIES environment variable not set")
            
            cookies = json.loads(cookies_json)
            context.add_cookies(cookies)
        except Exception as e:
            print(f"Error loading cookies: {e}")
            # Handle the error appropriately        
        
        # Create page
        page = context.new_page()
        
        try:

            # Get the new asins from the request
            
            data = request.get_json()
            if not data or 'asins' not in data:
                return jsonify({'error': 'No asins provided in the request'}), 400
            
            new_asins = data['asins']
            logging.info(f"ASINS Sent: {new_asins}")

            # Validate that keywords is a list of strings
            if not isinstance(new_asins, list) or not all(isinstance(k, str) for k in new_asins):
                return jsonify({'error': 'Asins must be a list of strings'}), 400
            
            # Update the keywords list
            asin_list = new_asins
        
            # Update the regex pattern
            pattern = re.compile(r'\b(' + '|'.join(map(re.escape, asin_list)) + r')\b', re.IGNORECASE)

            logging.info(f"Asins updated: {asin_list}")

            # First navigation to ensure we're authenticated

            print("Verifying authentication...")
            page.goto("https://members.helium10.com/dashboard")
            
            # Check if login was successful
            if "signin" in page.url:
                print("Error: Authentication failed")
                browser.close()
                return False
            
            print("Authentication verified!")
            
            # Process each ASIN
            for asin in asin_list:
                try:
                    print(f"Processing ASIN {asin}")
                    
                    # Navigate to Cerebro
                    print(f"  Navigating to Cerebro...")
                    page.goto('https://members.helium10.com/cerebro?accountId=2010218924', wait_until='networkidle')
                    
                    # Wait for the input field to be visible and type the ASIN
                    print(f"  Entering ASIN...")
                    page.wait_for_selector('.dAElQY')
                    page.fill('.dAElQY', asin)
                    page.keyboard.press('Enter')
                    
                    # Wait for and click the 'Get Keywords' button
                    print(f"  Clicking Get Keywords button...")
                    page.wait_for_selector('#CerebroSearchButtons button[data-testid="getkeywords"]')
                    page.click('#CerebroSearchButtons button[data-testid="getkeywords"]')
                    
                    # Wait for results to load
                    print(f"  Waiting for results...")
                    page.wait_for_selector('button[data-testid="exportdata"]', timeout=60000) # 60s timeout
                    
                    # Wait for and click the 'Export Data' button
                    print(f"  Clicking Export Data button...")
                    page.click('button[data-testid="exportdata"]')
                    
                    # Wait for and click the 'CSV Export' option
                    print(f"  Selecting CSV export...")
                    page.wait_for_selector('div[data-testid="csv"]')
                    
                    # Set up download expectation before clicking
                    with page.expect_download() as download_info:
                        page.click('div[data-testid="csv"]')
                    
                    # Handle the download
                    download = download_info.value
                    download_path = f"{asin}_export.csv"
                    download.save_as(download_path)
                    
                    print(f"✓ ASIN {asin} processed successfully. Downloaded to {download_path}")
                    
                except Exception as e:
                    print(f"× Error processing ASIN {asin}: {e}")
            
            print("All ASINs processed!")
            browser.close()
            return True
            
        except Exception as e:
            print(f"Error during processing: {e}")
            browser.close()
            return False


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


# Get all tasks
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    # In a real app, you would fetch from a database
    # For now, return sample data
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

# Create a new task
@app.route('/api/tasks', methods=['POST'])
def create_task():
    task_data = request.get_json()
    
    # Validate required fields
    if 'title' not in task_data:
        return jsonify({'error': 'Title is required'}), 400
    
    # In a real app, you would save to a database
    # For now, just return success with the data
    return jsonify({
        'success': True,
        'message': 'Task created successfully',
        'task': task_data
    }), 201

# Get a specific task
@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    # In a real app, you would fetch from a database
    # For now, return sample data if id matches
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

# Update a task
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task_data = request.get_json()
    
    # In a real app, you would update in a database
    # For now, just return success with the data
    return jsonify({
        'success': True,
        'message': f'Task {task_id} updated successfully',
        'task': task_data
    })

# Delete a task
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    # In a real app, you would delete from a database
    return jsonify({
        'success': True,
        'message': f'Task {task_id} deleted successfully'
    })




# Error handling for 404 errors
@app.errorhandler(404)
def not_found(e):
    logging.warning(f"404 error: {e}. Serving index.html.")
    return send_from_directory(app.static_folder, 'index.html')
if __name__ == '__main__':
    # Run the app on all interfaces and port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)