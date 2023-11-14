from flask import Flask, request, jsonify
from .service import find_suggestions_by_team, get_all_sprites
from flask_cors import CORS

app = Flask(__name__)
app.config['DEBUG'] = True
CORS(app)


@app.route('/suggestions', methods=['POST'])
def fetch_suggestions():

    data = request.get_json()
    team = data.get('team', [])
    suggestions = find_suggestions_by_team(team)
    return jsonify(suggestions)


@app.route('/sprites', methods=['GET'])
def fetch_sprites():

    sprites = get_all_sprites()
    return jsonify(sprites)


if __name__ == '__main__':
    app.run()
