import requests, sys, os
from utils import ManPageRetriever, FlagInfo
from flask import Flask, request, session, redirect, url_for, render_template, flash
from flask.helpers import jsonify

app = Flask(__name__)
app.debug = False
app.secret_key = os.environ.get('APP_SECRET_KEY', None)

GA_ACCOUNT = os.environ.get("GA_ACCOUNT", None)
GA_DOMAIN_NAME = os.environ.get("GA_DOMAIN_NAME", None)

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404

@app.errorhandler(500)
def error_encountered(error):
    return render_template('error.html'), 500

@app.route("/", methods=['GET'])
def index():
    return render_template("index.html")

@app.route("/search", methods=['POST'])
def search():
    command = request.form.get("command","")
    
    # Make sure there is a command
    if not command.split(" "):
        return jsonify(success=False)
    
    man_page = ManPageRetriever(command.split(" ")[0])
    man_page.run_retrieval()
        
    if man_page.is_error:
        return jsonify(success=False)

    # Grab the possible flags in our search
    command_flags = [flag for flag in FlagInfo.split_into_possible_flags(command)]
    # Find the descriptions of the flags we used in our search
    used_args = [(option, man_page.normalized_description_for(option)) for option in command_flags]

    return jsonify(success=True, used_args=used_args)

if __name__ == '__main__':
    app.run(host='0.0.0.0')