from flask import Flask, request, jsonify
from text_module import handle_text_query
from vision_module import handle_image
from audio_module import handle_audio

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Welcome to the Customer Support System!"

@app.route('/process', methods=['POST'])
def process_request():
    data = request.json
    return jsonify({"message": "Data received", "data": data})



@app.route('/text', methods=['POST'])
def text_endpoint():
    data = request.json
    return jsonify({"response": handle_text_query(data['text'])})

@app.route('/image', methods=['POST'])
def image_endpoint():
    file = request.files['image']
    file_path = f"uploads/{file.filename}"
    file.save(file_path)
    return jsonify({"response": handle_image(file_path)})

@app.route('/audio', methods=['POST'])
def audio_endpoint():
    file = request.files['audio']
    file_path = f"uploads/{file.filename}"
    file.save(file_path)
    return jsonify({"response": handle_audio(file_path)})

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)
if __name__ == "__main__":
    app.run(debug=True)