from flask import Flask, send_from_directory, request, jsonify
import random
from nepo import wiki_scrape

app = Flask(__name__)

# Path for our main Svelte page
@app.route("/")
def base():
    return send_from_directory('client/public', 'index.html')

# Path for all the static files (compiled JS/CSS, etc.)
@app.route("/<path:path>")
def home(path):
    return send_from_directory('client/public', path)


@app.route("/rand")
def hello():
    return str(random.randint(0, 100))

@app.route("/wiki")
def wiki():
    name = request.args.get('name')
    result = wiki_scrape(name)
    return result


if __name__ == "__main__":
    app.run(debug=True)
