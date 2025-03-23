from flask import Flask, request, jsonify, send_from_directory
import os
import csv
import json
from email import policy
from email.parser import BytesParser
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt', 'json', 'csv', 'eml'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ai_analyze_text(text):
    suspicious_keywords = ['hack', 'attack', 'malware', 'phishing', 'data breach', 'illegal']
    return [kw for kw in suspicious_keywords if kw in text.lower()] or "No suspicious keywords detected"

def analyze_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as txtfile:
        lines = txtfile.readlines()
    combined_text = ''.join(lines)
    ai_flags = ai_analyze_text(combined_text)
    return {"type": "TXT", "line_count": len(lines), "ai_flags": ai_flags, "data_preview": lines[:5]}

def analyze_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)
    combined_text = json.dumps(data)
    ai_flags = ai_analyze_text(combined_text)
    return {"type": "JSON", "keys": list(data[0].keys()) if isinstance(data, list) else None, "ai_flags": ai_flags, "data_preview": data[:5]}

def analyze_csv(file_path):
    data, vulnerabilities = [], []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
            for cell in row.values():
                if isinstance(cell, str) and cell.startswith(('=', '+', '-')):
                    vulnerabilities.append(f"Formula injection detected in cell: {cell}")
    combined_text = ' '.join(str(row) for row in data)
    ai_flags = ai_analyze_text(combined_text)
    return {"type": "CSV", "row_count": len(data), "ai_flags": ai_flags, "data_preview": data[:5], "vulnerabilities": vulnerabilities}

def analyze_email(file_path):
    with open(file_path, 'rb') as emlfile:
        msg = BytesParser(policy=policy.default).parse(emlfile)
    body = msg.get_body(preferencelist=('plain')).get_content() if msg.is_multipart() else msg.get_content()
    ai_flags = ai_analyze_text(body)
    return {"type": "EMAIL", "subject": msg['subject'], "from": msg['from'], "ai_flags": ai_flags, "body_preview": body[:200]}

def analyze_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.txt':
        return analyze_txt(file_path)
    elif ext == '.json':
        return analyze_json(file_path)
    elif ext == '.csv':
        return analyze_csv(file_path)
    elif ext == '.eml':
        return analyze_email(file_path)
    else:
        return {"error": "Unsupported file type"}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        result = analyze_file(file_path)
        os.remove(file_path)
        return jsonify(result)
    else:
        return jsonify({"error": "File type not allowed"}), 400

if __name__ == '__main__':
    app.run(debug=True)
