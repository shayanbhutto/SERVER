from flask import Flask, request, jsonify

app = Flask(__name__)

# Dictionary of valid username-password combinations
USERNAMES_PASSWORDS = {
    "shayan": "shayan11",
    "aziz": "aziz11",
    "sumira": "sumira11",
    "komal": "komal11"
}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if 'username' in data and 'password' in data:
        username = data['username'].lower()
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
