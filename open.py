import os
import subprocess
import platform

def check_virtualenv(env_name):
    return os.path.exists(os.path.join(env_name, 'bin', 'activate'))

def create_virtualenv(env_name):
    subprocess.run(['python', '-m', 'venv', env_name])

def activate_virtualenv(env_name):
    if platform.system() == 'Windows':
        activate_cmd = os.path.join(env_name, 'Scripts', 'activate')
        subprocess.run(f'call {activate_cmd}', shell=True)
    else:
        activate_cmd = os.path.join(env_name, 'bin', 'activate')
        subprocess.run(f'source {activate_cmd}', shell=True)

def check_customtkinter_exists(env_name):
    try:
        subprocess.run(['python', '-m', 'pip', 'list', '--format=columns'], check=True)
        pip_list_output = subprocess.check_output(['python', '-m', 'pip', 'list'], universal_newlines=True)
        return 'customtkinter' in pip_list_output
    except subprocess.CalledProcessError:
        return False

def install_customtkinter(env_name):
    print("Installing customtkinter...")
    subprocess.run(['python', '-m', 'pip', 'install', 'customtkinter'])

def run_main():
    subprocess.run(['python', 'main.py'])

def main():
    env_name = "myenv"

    if not check_virtualenv(env_name):
        print(f"Creating virtual environment '{env_name}'...")
        create_virtualenv(env_name)
        print("Virtual environment created.")

    activate_virtualenv(env_name)

    if not check_customtkinter_exists(env_name):
        install_customtkinter(env_name)

    # Now we can proceed with running main.py
    run_main()

if __name__ == "__main__":
    main()
