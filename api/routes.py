from flask import Blueprint, render_template, send_from_directory, request, jsonify
from glob import glob
from DiscordBot import bot
from utilities import DBOps
from datetime import datetime
import os, json



routes = Blueprint('routes', __name__)



@routes.route('/api/events', methods=['POST'])
async def events():
    post = request.json
    data: dict = json.loads(post)
    
    bot.dispatch('api_call', data)
    
    return jsonify({"message": "Data received successfully"}), 200
            


@routes.route('/')
def index():
    return render_template("index.html")



@routes.route('/api/matches/<path:filename>')
def serve_matchfiles(filename):
    dir = 'matches'
    return send_from_directory(dir, filename)



@routes.route('/matches')
def matches():
    pattern = 'api/matches/match_*.json'
    file_paths = glob(pattern)
    files = [os.path.basename(file_path) for file_path in file_paths]
    
    return render_template('matches.html', files=files)



@routes.route('/api/demos/<path:filename>')
def serve_demos(filename):
    dir = 'demos'
    return send_from_directory(dir, filename)



@routes.route('/demos', methods=['GET', 'POST'])
def demos():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file', 400
        
        file = request.files['file']
        if not file.filename.endswith('.bz2'):
            return 'Invalid file format.', 400
        
        timedate = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file.filename = f"{timedate}.dem.bz2"
        file.save("api/demos/" + file.filename)
        
        return 'Demo received', 200
    else:
        files = glob("api/demos/*.dem.bz2")
        file_names = [os.path.basename(file_path) for file_path in files]
        return render_template('demos.html', files=file_names)