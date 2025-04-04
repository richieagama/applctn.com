## License

[MIT License](LICENSE)

# Keyword Processor Application WIP

A web application that processes CSV files by filtering out rows containing specific negative keywords and combining the results into a single Excel file.

## Features

- Upload multiple CSV files at once via drag-and-drop or file browser
- Filter out rows containing specified negative keywords
- Combine filtered data into a single Excel spreadsheet
- Add, remove, and manage negative keywords through an intuitive UI
- Support for bulk keyword input
- Automatic download of processed Excel files

## Requirements

- Python 3.8 or higher
- Required Python packages (see Installation section)
- Modern web browser (Chrome, Firefox, Edge recommended)

## Setting Up on a New Machine

### 1. Clone the Repository

Open a terminal or command prompt and run:

```
git clone https://github.com/yourusername/keyword-processor.git
cd keyword-processor
```

### 2. Set Up Python Environment

#### Create a virtual environment:

On Windows:
```
python -m venv venv
venv\Scripts\activate
```

On macOS/Linux:
```
python -m venv venv
source venv/bin/activate
```

#### Install dependencies:

```
pip install -r requirements.txt
```

This will install all required packages:
- Flask (web server)
- Flask-CORS (for handling cross-origin requests)
- pandas (for data processing)
- openpyxl (for Excel file creation)

### 3. Run the Application

While in your virtual environment, start the Flask server:

```
python app.py
```

You should see output indicating the server is running, typically on http://localhost:5000

### 4. Access the Application

Open your web browser and navigate to:

```
http://localhost:5000
```

## Using the Application

### 1. Upload Files

- Drag and drop CSV files into the upload area, or click to browse and select files
- Only CSV files are accepted
- You can upload multiple files at once
- Each uploaded file must contain a "Keyword Phrase" column

### 2. Manage Keywords

- Add negative keywords in the right panel
- Type one keyword per line for bulk input
- Click "Add Keywords" to add them to the filter list
- Click the "x" on any keyword cute choice chips to remove it
- Use "Clear All" to remove all keywords

### 3. Trust the Process SEO Tool

- Click "Trust the Process (Submit button)" to start filtering and combining your data
- The application will filter out any rows where the "Keyword Phrase" column contains any of your negative keywords
- The application will filter out any duplicate rows where the "Keyword Phrase" matches
- The file will automatically download when processing is complete
- You can process thousands of files, my python is solid

## Troubleshooting

- If files aren't uploading, ensure they are valid CSV files
- If it fails with one file that's beacuse the app is trash rn

## Development Notes

- Backend: Flask Python web server
- Frontend: React with Material UI components
- Core functionality: SEO for Dummys Online Edition | All Rights Reserved to Richard David Agama



END OF READ