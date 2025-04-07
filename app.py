from flask import Flask, render_template, request
import os
import subprocess
import json
import time
from PyPDF2 import PdfReader
from docx import Document

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    file = request.files['file']
    filename = file.filename
    ext = filename.split('.')[-1].lower()
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Convert to plain text
    text = ""
    if ext == 'txt':
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    elif ext == 'pdf':
        reader = PdfReader(filepath)
        text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    elif ext == 'docx':
        doc = Document(filepath)
        text = "\n".join([p.text for p in doc.paragraphs])
    else:
        return "Unsupported file type!", 400

    input_path = os.path.join(app.config['UPLOAD_FOLDER'], 'input.txt')
    with open(input_path, 'w', encoding='utf-8') as f:
        f.write(text)

    # Time normal count
    start_normal = time.time()
    normal_count = len(text.split())
    end_normal = time.time()

    # Time MPI word count
    start_mpi = time.time()
    subprocess.run(['mpiexec', '-n', '4', 'python', 'mpi_wordcount.py'])
    end_mpi = time.time()

    with open('output.json', 'r') as f:
        mpi_result = json.load(f)

    result = {
        'mpi_count': mpi_result['total_words'],
        'normal_count': normal_count,
        'mpi_time': round(end_mpi - start_mpi, 4),
        'normal_time': round(end_normal - start_normal, 4)
    }

    return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
