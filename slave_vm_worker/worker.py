import random

from flask import Flask

app = Flask(__name__)

quotes_list = ["Second thoughts are the reinforcements of the first thoughts you were trying to ignore (Steve Piccus)", "If I don't succeed, then let seed suck me. (Steve Piccus)"];

@app.route('/')
def index():
    return random.choice(quotes_list)

if __name__ == '__main__':
    app.run(debug='True', host='0.0.0.0', port=5000);