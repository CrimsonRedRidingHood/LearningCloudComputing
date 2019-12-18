import os
import subprocess
import time

from flask import Flask
from subprocess import PIPE

is_slave_running = False

aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

slave_start_playbook = './vm_manager/slave_start.yml'

app = Flask(__name__)

def terminate_slave():
    subprocess.run(['ansible-playbook', './vm_manager/slave_terminate.yml'])

def start_slave():
    start_time = time.time()
    # used to pass AWS keys to the ansible-playbook
    #extra_vars_argument = '"aws_access_key=' + aws_access_key + ' ' + 'aws_secret_key=' + aws_secret_key + '"'
    extra_vars_argument = f'{{"aws_access_key":"{aws_access_key}","aws_secret_key":"{aws_secret_key}"}}'
    # DEBUG
    print(extra_vars_argument)
    result = subprocess.run(['ansible-playbook', slave_start_playbook, '--extra-vars', extra_vars_argument], stdout=PIPE, stderr=PIPE)
    if result.returncode != 0:
        print('stdout:', result.stdout.decode('utf-8'))
        print('stderr:', result.stderr.decode('utf-8'))
        return
    slave_ip = re.findall(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b', result.stdout.decode('utf-8'))[0]
    print('slave vm with public ip', slave_ip, 'has been started')
    return slave_ip
    

@app.route('/')
def index():
    return 'Nice to meet you'
    
@app.route('/start')
def debug_start_slave():
    return start_slave()
    
@app.route('/stop')
def debug_stop_slave():
    terminate_slave()
    return 'Slave has been terminated'
    
if __name__ == '__main__':
    app.run(debug='True', host='0.0.0.0', port=5000);