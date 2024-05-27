from flask import Flask, request, jsonify
from PIL import Image
import os

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        # Save the file temporarily
        file_path = os.path.join('/tmp', file.filename)
        file.save(file_path)
        
        # Open the image and get size and format
        with Image.open(file_path) as img:
            size = img.size  # (width, height)
            extension = img.format  # e.g., 'JPEG', 'PNG'
        
        # Clean up
        os.remove(file_path)
        
        return jsonify({
            "width": size[0],
            "height": size[1],
            "extension": extension
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
