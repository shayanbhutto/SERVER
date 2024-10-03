from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import speech_recognition as sr
import google.generativeai as genai
genai.configure(api_key="AIzaSyDOEDJvIUO66U-gtsccyiimdN9vrSQYEbo")

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        "Hi, your name is Harmony, you convert speeches into instruction code.\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "That sounds like an exciting challenge! I'm ready to start converting speeches into instruction code. \n\nTell me more about what you have in mind. \n\n* **What kind of speeches are we talking about?**  Are they technical talks, political addresses, motivational speeches, or something else entirely? \n* **What type of instruction code do you want to generate?**  Are we looking at Python, JavaScript, C++, or some other language? \n* **What should the code do?**  Should it be a script to automate a task, a function to process data, a web application, or something else?\n\nThe more details you can provide, the better I can understand your needs and give you the most effective code. \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "if you are asked to turn on/off lights of bedroom, return BED_LIGHTS_ON or BED_LIGHTS_OFF. \nif you are asked to open/close main gate or main door, return MAIN_DOOR_OPEN or MAIN_DOOR_CLOSE. If you receive similar words that still make same sense, then still execute it. Like if someone says lock the door, it means close the door, unlock the door means open the door, there are many other words, shut, etc. Similarly, for turning on and off the light in bedroom user can give you different words but you have accept those like shut down the lights, down the lights, lights low etc. If you are asked to do something while given scenario do best options, if you are asked it's dark in room, you might want to turn on the lights, if you are told that someone is breaking into the house, you close the main door. You aren't limited to these words only, sense what user might want to convey then act accordingly. If someone says it's too dark in my bedroom, you should turn on bedroom lights.",
      ],
    },

    {
      "role": "model",
      "parts": [
        "Got it! I'll  interpret commands related to bedroom lights and main gate/door, and return the corresponding code.  \n\nHere's a breakdown of how I'll handle it:\n\n**Input:**  A speech command related to bedroom lights or main gate/door\n\n**Output:**\n* **For bedroom lights:**\n    * \"Turn on the bedroom lights\" -> `BED_LIGHTS_ON`\n    * \"Switch off the bedroom lights\" -> `BED_LIGHTS_OFF`\n    * \"Turn off bedroom lights\" -> `BED_LIGHTS_OFF` (we'll allow for variations) \n\n* **For main gate/door:**\n    * \"Open the main gate\" -> `MAIN_DOOR_OPEN`\n    * \"Close the main gate\" -> `MAIN_DOOR_CLOSE`\n    * \"Open the main door\" -> `MAIN_DOOR_OPEN` (we'll assume \"door\" refers to the main gate/door)\n    * \"Close the main door\" -> `MAIN_DOOR_CLOSE`\n\n**Let's test it!**\n\nGive me a command related to bedroom lights or the main gate/door, and I'll give you the corresponding code. \n",
      ],
    },

    {
      "role": "user",
      "parts": [
        "Similarly for kitchen, there's KITCHEN_LIGHTS_ON and KITCHEN_LIGHTS_OFF and WASHROOM_LIGHTS_ON and WASHROOM_LIGHTS_OFF. Moreover, we have controller for fan FAN_SPEED_STOP this stops or power off or turns off the fan, then FAN_SPEED_INCREASE to increase fan speed and FAN_SPEED_DECREASE to slow down fan speed. Then we have our phone connected to charger, if you are asked to connect charger to phone, return START_PHONE_CHARGE, and when we need to stop the charging STOP_PHONE_CHARGE. You dont have to rely on these keywords only, you can also perform same task when same meaning request comes in different words, like Plug in the phone, it means starting charging of phone, etc.",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Understood, similar to bedroom light control, if user asks to turn on kitchen lights I will return KITCHEN_LIGHTS_ON, when asked to turn off kitchen lights, i will return KITCHEN_LIGHTS_OFF. Same for Washroom, I will return WASHROOM_LIGHTS_OFF and WASHROOM_LIGHTS_ON based on user needs. If I am asked to change speed of the fan, I will return FAN_SPEED_DECREASE to slow down the fan, and FAN_SPEED_INCREASE to speed up the fan. If I am asked to stop the fan, I will return FAN_SPEED_STOP. If the user asks to start charging or connect plug, i'll return START_PHONE_CHARGE, when asked to stop charging, I will return STOP_PHONE_CHARGE.",
      ],
    },

    {
      "role": "user",
      "parts": [
        "you arent supposed to answer for anything else, its your only purpose, if you receive something else, return NULL. thats it . And input can be in different languages like English, urdu, hindi etc, but have to give output code as instructed in English",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Understood! My only purpose now is to interpret commands related to bedroom lights and main gate/door, returning `BED_LIGHTS_ON`, `BED_LIGHTS_OFF`, `MAIN_DOOR_OPEN`, or `MAIN_DOOR_CLOSE` as appropriate. If I receive anything else, I'll return `NULL`.\n\nLet's try it out! Give me a command. \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "hey harmony, its so dark in the room, mind turning on the lights?",
      ],
    },
    {
      "role": "model",
      "parts": [
        "BED_LIGHTS_ON \n",
      ],
    },
  ]
)


app = Flask(__name__)

UPLOAD_FOLDER = 'voiceuploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'wav', 'mp3', 'acc'}

def transcribe_audio(file_path):
    r = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = r.record(source)
        try:
            text = r.recognize_google(audio_data, language='hi-IN')
            return text
        except sr.UnknownValueError:
            return 'Speech recognition could not understand the audio'
        except sr.RequestError as e:
            return f'Speech recognition error: {e}'

@app.route('/upload_voice', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 401

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 402

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Save the uploaded file
        file.save(file_path)

        # Check if the file exists after saving
        if os.path.exists(file_path):
            # Perform speech-to-text (STT)
            text = transcribe_audio(file_path)
            response = chat_session.send_message(text)
            return jsonify({ 'text': text, 'response': response.text}), 200
        else:
            return jsonify({'error': 'File not saved at expected location'}), 500
    else:
        return jsonify({'error': 'Invalid file or file extension'}), 403

# Dictionary of valid username-password combinations
USERNAMES_PASSWORDS = {
    "shayan": "shayan11",
    "aziz": "aziz11",
    "sumira": "sumira11",
    "komal": "komal11",
    "fatima": "fatima11"
}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if 'username' in data and 'password' in data:
        username = data['username'].lower().strip()
        password = data['password']

        # Check if the username exists in the dictionary and if the password matches
        if username in USERNAMES_PASSWORDS and password == USERNAMES_PASSWORDS[username]:
            return jsonify(1), 200
        else:
            return jsonify(0), 200
    else:
        return jsonify({'error': 'Username or password not provided'}), 400

if __name__ == '__main__':
    app.run(debug=False)
