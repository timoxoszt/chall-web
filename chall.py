import flask
import requests
import os
import urllib
import subprocess
from waitress import serve

app = flask.Flask(__name__)
home = os.path.dirname(os.path.realpath(__file__))

@app.route('/', methods=['GET'])
def index():
	return "<a href=\"/getData?f=/fus/data/1.txt\">1.txt</a></br><a href=\"/getData?f=/fus/data/2.txt\">2.txt</a></br><a href=\"/getData?f=/fus/data/3.txt\">3.txt</a></br><a href=\"/getData?f=/fus/data/4.txt\">4.txt</a></br><a href=\"/getData?f=/fus/data/5.txt\">5.txt</a></br>"

@app.route('/getData', methods=['GET'])
def getLog():
	log_file = flask.request.args.get('f')
	if (log_file.startswith('/fus/data')):
		return flask.send_file(log_file, mimetype='text/plain', as_attachment=False)
	else:
		return ({'status': 'invalid path'},200)

# run script to crawl data
@app.route('/runScript')
def runScript():
	json = flask.request.json
	msg = start(json)
	return ({'status': msg},200)

def check_script_dup(scripts, command_log, json):
	try:
		script_parent_dir = scripts + '/' + json['dir']
		script_path = script_parent_dir + '/' + json['name']
	except:
		return "missing dir and name"
	if os.path.exists(script_path):
		return "duplicate script"
	else:
		if not os.path.exists(script_parent_dir):
			os.makedirs(script_parent_dir)
		return download_script(script_path, command_log, json)

def download_script(script_path, command_log, json):
	try:
		script_link = json['url']
	except:
		return "missing url"
	# don't trust anyone
	if (urllib.parse.urlparse(script_link).netloc == "localhost:8888"):
		result = requests.get(script_link)
		with open(script_path, 'wb') as f:
			f.write(result.content)
			run_script(script_path, command_log)
	else:
		return "invalid script link"

def run_script(script_path, command_log):
	lf = open(command_log, 'wb+')
	print('comand',command_log)
	command = subprocess.Popen(['bash', script_path], stderr=lf, stdout=lf, universal_newlines=True)
	return "Run successfully"

def start(json):
	scripts = home + '/scripts'
	log = home + '/logs'
	if not os.path.exists(scripts):
		os.makedirs(scripts)
	if not os.path.exists(log):
		os.makedirs(log)
	try:
		command_log = log + '/' + json['command_log'] + '.txt'
	except:
		return "missing command_log"
	msg = check_script_dup(scripts, command_log, json)
	return msg

if __name__ == '__main__':
	serve(app, host='0.0.0.0', port=8888)
