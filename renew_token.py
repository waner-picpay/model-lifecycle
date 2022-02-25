import os
import urllib.parse
import sys

CREDENTIAL_FILE = os.getenv("HOME") + "/.aws/credentials"
ENV_FILE = os.getcwd() + "/.env"
ENV_LIST = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"]

profile = sys.argv[1]

def process_aws_file(credentials_file):
    credentials = {}
    copy_line = False
    for line in credentials_file:
        if copy_line and len(line.strip()) != 0:
            credentials[line.split("=")[0].replace(' ', '')] = line.split("=")[1].strip()

        if line.find('[' + profile + ']') != -1: #find profile
            copy_line = True
        elif len(line.strip()) == 0:
            copy_line = False

    return credentials

# remove existing envs and create all new envs
def process_envs(env_data):
    new_env = []
    for line in env_data:
        count = 0
        for e in ENV_LIST:
            if line.find(e) != -1:
                count += 1
                
        if count == 0:
            new_env.append(line)
                
    new_env[-1] = new_env[-1].strip() + '\n'
    for e in ENV_LIST:
        new_env.append(e + '=\n')
    
    return new_env

def process_env_file(env_file):
    env_data = env_file.readlines()
    return process_envs(env_data)

def write_env(env_file, credentials, env_data):
    # find new empty envs and fill them
    for line in env_data:
        if line.find("AWS_ACCESS_KEY_ID") != -1:
            variable_name = line.split('=')[0]
            line = variable_name + '=' + credentials['aws_access_key_id'] + '\n'
        elif line.find("AWS_SECRET_ACCESS_KEY") != -1:
            variable_name = line.split('=')[0]
            line = variable_name + '=' + credentials['aws_secret_access_key']+ '\n'
        elif line.find("AWS_SESSION_TOKEN") != -1:
            variable_name = line.split('=')[0]
            line = variable_name + '=' + credentials['aws_session_token'] + '\n'
        
        env_file.write(line)


credentials = {}
with open(CREDENTIAL_FILE, 'r') as credentials_file:
  credentials = process_aws_file(credentials_file)

with open(ENV_FILE, 'r') as env_file:
    env_data = process_env_file(env_file)

with open(ENV_FILE, 'w') as env_file:
    write_env(env_file, credentials, env_data)