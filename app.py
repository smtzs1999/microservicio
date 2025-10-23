# app.py
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Hola desde el microservicio!"})

@app.route("/sum", methods=["POST"])
def sum_numbers():
    data = request.get_json()
    resultado = data.get("a", 0) + data.get("b", 0)
    return jsonify({"resultado": resultado})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
