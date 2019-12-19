import os
import subprocess
import time
import re
import requests
import threading
import paramiko
import socket

from flask import Flask, request, send_from_directory
from subprocess import PIPE

is_slave_running = False

aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

slave_start_playbook = './vm_manager/slave_start.yml'
slave_terminate_playbook = './vm_manager/slave_terminate.yml'

slave_credentials_file = './SlaveVMSSHCredentials.pem'

slave_worker_file = './slave_vm_worker/worker.py'

app = Flask(__name__, static_url_path='/')

def terminate_slave():
    subprocess.run(['ansible-playbook', slave_terminate_playbook])

def copy_server_to_slave(slave_server_address):
    returncode = 1
    while returncode != 0:
        returncode = subprocess.run(["sudo", "scp", "-i", slave_credentials_file, "-o", 'StrictHostKeyChecking=no', slave_worker_file, "ubuntu@" + slave_server_address + ":~/worker.py"]).returncode
    
def run_slave_server(slave_server_address):
    ssh_connection = paramiko.SSHClient()
    ssh_connection.load_system_host_keys()
    ssh_connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print('Host keys loaded')
    ssh_connection.connect(slave_server_address, username="ubuntu", key_filename=slave_credentials_file)
    print('Successfully connected')
    #ssh_stdin, ssh_stdout, ssh_stderr = ssh_connection.exec_command("sudo apt-get update")
    ssh_stdin, ssh_stdout, ssh_stderr = ssh_connection.exec_command("sudo python3 ~/worker.py")

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
    print(result.stdout.decode('utf-8'))
    global slave_ip
    slave_ip = re.findall(r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b', result.stdout.decode('utf-8'))[0]
    print('slave vm with public ip', slave_ip, 'has been started')
    slave_server_address = "ec2-" + slave_ip.replace('.','-') + ".us-east-2.compute.amazonaws.com"
    copy_server_to_slave(slave_server_address)
    slave_server_runner = threading.Thread(target=run_slave_server, args=(slave_server_address,))
    slave_server_runner.start()
    
    time.sleep(5)
    
    global slave_socket
    slave_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    is_socket_connected = False
    
    # connecting to the slave using sockets
    while not is_socket_connected:
        is_socket_connected = True
        try:
            slave_socket.connect((slave_ip, 5000))
        except:
            is_socket_connected = False
    
    return slave_ip

@app.route('/')
def index():
    return send_from_directory('', 'index.html')
    
@app.route('/js/<path:path_to_file>')
def return_script(path_to_file):
    return send_from_directory('js', path_to_file)

@app.route('/css/<path:path_to_file>')
def return_style(path_to_file):
    return send_from_directory('css', path_to_file)
    
@app.route('/start')
def debug_start_slave():
    return start_slave()
    
@app.route('/stop')
def debug_stop_slave():
    terminate_slave()
    return 'Slave has been terminated'
    
@app.route('/get_quote')
def get_quote():
    slave_socket.sendall('1'.encode())
    data = slave_socket.recv(1024)
    return data.decode()
    
if __name__ == '__main__':
    app.run(debug='True', host='0.0.0.0', port=5000);