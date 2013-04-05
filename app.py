import os
from utils import ManPageRetriever, OptionInfo
from flask import Flask, request, render_template
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
    return render_template("index.html", ga_account=GA_ACCOUNT, ga_domain_name=GA_DOMAIN_NAME)

@app.route("/search", methods=['POST'])
def search():
    command = request.form.get("command","")
    
    # Make sure there is a command
    if not command.split(" "):
        return jsonify(success=False, error_message="Invalid command")
    
    man_page = ManPageRetriever(command.split(" ")[0])
    
    if not man_page.supports_man_page():
        return jsonify(success=False, error_message="Sorry, we do not support that command yet")

    man_page.run_retrieval()
        
    # Grab the possible options in our search
    command_options = [flag for flag in OptionInfo.split_into_possible_options(command)]
    # Find the descriptions of the options we used in our search
    used_args = [man_page.normalized_result_for(option) for option in command_options]

    return jsonify(success=True, used_args=used_args)

if __name__ == '__main__':
    app.run(host='0.0.0.0')