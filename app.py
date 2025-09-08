import os
import spacy
import requests
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, flash

# Make sure you have your legal_ner.py file in the same directory
from legal_ner import extract_entities_from_judgment_text

# --- App and Model Configuration ---
app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'your_super_secret_key'  # Needed for flashing messages
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Load Models Once on Startup ---
# This is crucial for performance, so models are not reloaded on every request.
print("Loading NLP models... This may take a moment.")
try:
    legal_nlp = spacy.load('en_legal_ner_trf')
    preamble_splitting_nlp = spacy.load('en_core_web_sm')
    print("Models loaded successfully!")
except OSError:
    print("Error loading models. Please ensure they are installed correctly.")
    legal_nlp = None
    preamble_splitting_nlp = None

# --- Main Routes ---
@app.route('/')
def index():
    """Renders the main upload page."""
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract():
    """Handles both PDF and URL submissions for entity extraction."""
    if not legal_nlp or not preamble_splitting_nlp:
        flash("NLP models are not loaded. Cannot process request.", "error")
        return render_template('index.html')

    text_to_process = ""
    source = ""

    # --- CHANGE HERE for PDF vs. Web Scraping ---
    
    # 1. Logic for PDF Upload
    if 'pdf_file' in request.files and request.files['pdf_file'].filename != '':
        file = request.files['pdf_file']
        if file and file.filename.endswith('.pdf'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            # Extract text from the saved PDF
            try:
                with fitz.open(filepath) as doc:
                    for page in doc:
                        text_to_process += page.get_text()
                source = f"PDF: {file.filename}"
            except Exception as e:
                flash(f"Error reading PDF file: {e}", "error")
                return render_template('index.html')
            finally:
                os.remove(filepath) # Clean up the uploaded file
        else:
            flash("Invalid file type. Please upload a PDF.", "error")
            return render_template('index.html')

    # 2. Logic for Web Scraping
    elif 'url' in request.form and request.form['url'] != '':
        url = request.form['url']
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status() # Raise an exception for bad status codes
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script_or_style in soup(['script', 'style']):
                script_or_style.decompose()
            
            text_to_process = soup.get_text(separator='\n', strip=True)
            source = f"URL: {url}"
        except requests.RequestException as e:
            flash(f"Error fetching URL: {e}", "error")
            return render_template('index.html')

    else:
        flash("No input provided. Please upload a PDF or enter a URL.", "warning")
        return render_template('index.html')

    # --- Run NER model on the extracted text ---
    if text_to_process:
        print(f"Processing text from {source}...")
        combined_doc = extract_entities_from_judgment_text(
            text_to_process,
            legal_nlp,
            preamble_splitting_nlp,
            text_type='sent',
            do_postprocess=True
        )
        entities = [(ent.text, ent.label_) for ent in combined_doc.ents]
        return render_template('results.html', entities=entities, source=source)
    
    flash("Could not extract any text from the provided source.", "error")
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)