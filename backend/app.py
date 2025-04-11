from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from playwright.sync_api import sync_playwright

import pandas as pd
import os
import re
import logging
import json
import time

from io import BytesIO
import zipfile
from datetime import datetime

EXPORT_DIR = os.path.join(os.getcwd(), 'exports')
os.makedirs(EXPORT_DIR, exist_ok=True)


# Configure logging
logging.basicConfig(level=logging.INFO)
app = Flask(__name__, static_folder='static', static_url_path='')

CORS(app)
# List of negative keywords
negative_keywords = [
    "sunco","chandelier","home depot"
]

# List of asins 
asin_list = ["B0D9N92BFX","B0CWD455P1","B0CHVMH3J9"]

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
    
    # Ensure export directory exists in both local and Render environments
    EXPORT_DIR = os.path.join(os.getcwd(), 'exports')
    os.makedirs(EXPORT_DIR, exist_ok=True)
    
    # Create a screenshots directory for debugging
    SCREENSHOTS_DIR = os.path.join(os.getcwd(), 'screenshots')
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    
    # Maximum number of retries per ASIN
    MAX_RETRIES = 3
    # Longer timeout values in milliseconds
    NAVIGATION_TIMEOUT = 120000
    SELECTOR_TIMEOUT = 90000
    
    # Track successful and failed ASINs
    successful_asins = []
    failed_asins = []
    
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--single-process',
                '--js-flags=--max-old-space-size=256',
                '--memory-pressure-off',
                '--disk-cache-size=0'
            ]
        )
        
        # Create context
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        
        # Try loading cookies from file first, fall back to environment variable
        # Load cookies from file 
        # with open("helium10_auth_cookies.json", "r") as f:
        #    cookies = json.load(f)
        # context.add_cookies(cookies)

        # Load cookies from environment variable
        try:
            cookies_json = os.environ.get("HELIUM10_COOKIES")
            if not cookies_json:
                raise Exception("HELIUM10_COOKIES environment variable not set")
            
            #print(f"cookie: {cookies_json}")
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
            logging.info(f"ASINS to process: {new_asins}")
            
            # Validate that asins is a list of strings
            if not isinstance(new_asins, list) or not all(isinstance(k, str) for k in new_asins):
                return jsonify({'error': 'Asins must be a list of strings'}), 400
            
            # Update the asins list
            asin_list = new_asins
            pattern = re.compile(r'\b(' + '|'.join(map(re.escape, asin_list)) + r')\b', re.IGNORECASE)
            
            # First navigation to ensure we're authenticated
            print("Verifying authentication...")
            logging.info("Verifying authentication...")
            
            # Take screenshot of initial state
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f"1_initial_state_{timestamp}.png"))
            
            page.goto("https://members.helium10.com/dashboard", timeout=NAVIGATION_TIMEOUT)
            
            # Take screenshot after navigation
            page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f"2_auth_check_{timestamp}.png"))
            
            # Check if login was successful
            if "signin" in page.url:
                print("Error: Authentication failed")
                logging.error("Authentication failed")
                page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f"auth_failed_{timestamp}.png"))
                browser.close()
                return jsonify({
                    'success': False,
                    'message': 'Authentication failed',
                    'failed_asins': asin_list
                }), 401
            
            print("Authentication verified!")
            logging.info("Authentication verified!")
            
            # Process each ASIN with retries
            for asin in asin_list:
                retry_count = 0
                success = False
                
                while retry_count < MAX_RETRIES and not success:
                    try:
                        if retry_count > 0:
                            print(f"Retry #{retry_count} for ASIN {asin}")
                            logging.info(f"Retry #{retry_count} for ASIN {asin}")
                        else:
                            print(f"Processing ASIN {asin}")
                            logging.info(f"Processing ASIN {asin}")
                        
                        # Navigate to Cerebro
                        print(f"  Navigating to Cerebro...")
                        logging.info(f"  Navigating to Cerebro for {asin}...")
                       
                        page.goto('https://members.helium10.com/cerebro?accountId=2010218924', 
                                wait_until='networkidle', timeout=NAVIGATION_TIMEOUT)
                        
                        # Screenshot after navigation to Cerebro
                        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f"3_{asin}_cerebro_page_try{retry_count}.png"))
                        
                        # Wait for the input field to be visible and type the ASIN
                        print(f"  Entering ASIN...")
                        logging.info(f"  Entering ASIN {asin}...")
                        
                        page.wait_for_selector('.dAElQY', timeout=SELECTOR_TIMEOUT)
                        page.fill('.dAElQY', asin)
                        
                        # Screenshot after filling ASIN
                        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f"4_{asin}_filled_try{retry_count}.png"))
                        
                        page.keyboard.press('Enter')
                        time.sleep(2)  # Small delay after Enter
                        
                        # Screenshot after pressing Enter
                        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f"5_{asin}_after_enter_try{retry_count}.png"))
                        
                        # Wait for and click the 'Get Keywords' button
                        print(f"  Clicking Get Keywords button...")
                        logging.info(f"  Clicking Get Keywords button for {asin}...")
                        
                        # Try to get keywords with a longer timeout
                        keywords_button = page.wait_for_selector(
                            '#CerebroSearchButtons button[data-testid="getkeywords"]',
                            timeout=SELECTOR_TIMEOUT
                        )
                        
                        # Screenshot before clicking keywords button
                        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f"6_{asin}_before_keywords_try{retry_count}.png"))
                        
                        keywords_button.click()
                        
                        # Wait for results to load
                        print(f"  Waiting for results...")
                        logging.info(f"  Waiting for results for {asin}...")
                        
                        # Screenshot after clicking keywords button
                        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f"7_{asin}_after_keywords_try{retry_count}.png"))
                        
                        # Wait for export button with extra long timeout
                        export_button = page.wait_for_selector(
                            'button[data-testid="exportdata"]', 
                            timeout=SELECTOR_TIMEOUT * 2  # Double timeout for results
                        )
                        
                        # Screenshot after results loaded
                        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f"8_{asin}_results_loaded_try{retry_count}.png"))
                        
                        # Wait for and click the 'Export Data' button
                        print(f"  Clicking Export Data button...")
                        logging.info(f"  Clicking Export Data button for {asin}...")
                        export_button.click()
                        
                        # Screenshot after clicking export
                        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f"9_{asin}_after_export_click_try{retry_count}.png"))
                        
                        # Wait for and click the 'CSV Export' option
                        print(f"  Selecting CSV export...")
                        logging.info(f"  Selecting CSV export for {asin}...")
                        
                        csv_button = page.wait_for_selector('div[data-testid="csv"]', timeout=SELECTOR_TIMEOUT)
                        
                        # Screenshot before clicking CSV
                        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f"10_{asin}_before_csv_try{retry_count}.png"))
                        
                        # Set up download expectation before clicking
                        with page.expect_download(timeout=SELECTOR_TIMEOUT) as download_info:
                            csv_button.click()
                        
                        # Handle the download
                        download = download_info.value
                        download_path = os.path.join(EXPORT_DIR, f"{asin}_export.csv")
                        download.save_as(download_path)
                        
                        # Verify file exists and has content
                        if os.path.exists(download_path) and os.path.getsize(download_path) > 0:
                            print(f"✓ ASIN {asin} processed successfully. Downloaded to {download_path}")
                            logging.info(f"✓ ASIN {asin} processed successfully. Downloaded to {download_path}")
                            
                            success = True
                            successful_asins.append(asin)
                        else:
                            raise Exception(f"Download file is empty or missing for {asin}")
                        
                    except Exception as e:
                        retry_count += 1
                        error_msg = f"Error processing ASIN {asin} (attempt {retry_count}/{MAX_RETRIES}): {e}"
                        print(f"× {error_msg}")
                        logging.error(error_msg)
                        
                        # Take an error screenshot
                        try:
                            page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f"error_{asin}_try{retry_count}.png"))
                        except:
                            pass
                        
                        # If we've reached max retries, add to failed list
                        if retry_count >= MAX_RETRIES:
                            failed_asins.append({
                                "asin": asin,
                                "error": str(e)
                            })
                        
                        # Add a delay before retry
                        time.sleep(5)
                
            # Print summary of results
            print(f"ASINs processed successfully: {successful_asins}")
            print(f"ASINs that failed: {failed_asins}")
            logging.info(f"ASINs processed successfully: {successful_asins}")
            logging.info(f"ASINs that failed: {failed_asins}")
            
            # Final screenshot
            page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f"final_state_{timestamp}.png"))
            
            browser.close()
            return jsonify({
                'success': len(failed_asins) == 0,
                'message': 'Processing completed',
                'successful_asins': successful_asins,
                'failed_asins': [f["asin"] for f in failed_asins],
                'error_details': failed_asins,
                'total_successful': len(successful_asins),
                'total_failed': len(failed_asins),
                'screenshots_dir': SCREENSHOTS_DIR,
                'exports_dir': EXPORT_DIR
            }), 200
            
        except Exception as e:
            print(f"Error during processing: {e}")
            logging.error(f"Error during processing: {e}")
            
            # Take final error screenshot
            try:
                page.screenshot(path=os.path.join(SCREENSHOTS_DIR, f"fatal_error_{timestamp}.png"))
            except:
                pass
                
            browser.close()
            return jsonify({
                'success': False,
                'message': f'Error during processing: {str(e)}',
                'successful_asins': successful_asins,
                'failed_asins': [a for a in asin_list if a not in successful_asins]
            }), 500


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


@app.route('/download-exports', methods=['GET'])
def download_exports():
    try:
        # Get a list of the CSV files
        csv_files = [f for f in os.listdir(EXPORT_DIR) if f.endswith('_export.csv')]
        
        if not csv_files:
            return jsonify({'error': 'No export files found'}), 404
        
        # Create a ZIP file in memory
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for csv_file in csv_files:
                file_path = os.path.join(EXPORT_DIR, csv_file)
                zipf.write(file_path, csv_file)
        
        # Seek to the beginning of the BytesIO object
        memory_file.seek(0)
        
        # Send the ZIP file as a response
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'helium10_exports_{timestamp}.zip'
        )
    
    except Exception as e:
        logging.exception(f"Error creating ZIP file: {str(e)}")
        return jsonify({'error': str(e)}), 500


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