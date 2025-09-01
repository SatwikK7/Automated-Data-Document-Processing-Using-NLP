from flask import Flask, request, render_template, send_from_directory, jsonify
import os
from pdf_to_images import crop_and_save_signatures_from_pdf
from verify import SignatureVerifier  # <-- your deep learning verifier

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SIGNATURE_FOLDER'] = 'static/signatures'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SIGNATURE_FOLDER'], exist_ok=True)

# Load verifier once (fast)
verifier = SignatureVerifier()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'pdf' not in request.files:
        return "No file part", 400
    file = request.files['pdf']
    if file.filename == '':
        return "No selected file", 400
    if not file.filename.endswith('.pdf'):
        return "Invalid file type. Please upload a PDF.", 400

    # Save uploaded PDF
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(pdf_path)

    # Run detection + crop
    model_path = "best.pt"  # YOLOv8 model path
    output_folder = app.config['SIGNATURE_FOLDER']
    crop_and_save_signatures_from_pdf(model_path, pdf_path, output_folder, confidence_threshold=0.25, dpi=300)

    # Find all signatures saved for this PDF
    pdf_name = os.path.splitext(file.filename)[0]
    signatures = [f for f in os.listdir(output_folder) if f.startswith(pdf_name)]

    results = []
    verified = False

    for sig_file in signatures:
        sig_path = os.path.join(output_folder, sig_file)

        # Extract counterparty name from filename convention: "Counterparty_something_page_x_signature_x.jpg"
        # Example: "JPMC_doc1_page_01_signature_01.jpg"
        counterparty = sig_file.split("_")[0]

        result = verifier.verify(sig_path, counterparty)
        results.append({
            "file": sig_file,
            "counterparty": counterparty,
            "distance": result["distance"],
            "threshold": result["threshold"],
            "result": result["result"]
        })

        if result["result"] == "genuine":
            verified = True

    response = {
        "verified": verified,
        "details": results
    }
    return jsonify(response)

@app.route('/signatures/<path:filename>')
def get_signature(filename):
    return send_from_directory(app.config['SIGNATURE_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
  
