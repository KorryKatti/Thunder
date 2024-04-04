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

def run_main():
    subprocess.run(['python', 'main.py'])

def run_updater():
    subprocess.run(['python', 'updater.py'])

def main():
    env_name = "myenv"

    if not check_virtualenv(env_name):
        print(f"Creating virtual environment '{env_name}'...")
        create_virtualenv(env_name)
        print("Virtual environment created.")

    activate_virtualenv(env_name)

    if os.path.exists(os.path.join(env_name, 'lib', 'python3.x', 'site-packages', 'customtkinter', '__init__.py')):
        print("Module 'customtkinter' found.")
        run_main()
    else:
        print("Module 'customtkinter' not found.")
        run_updater()

if __name__ == "__main__":
    main()
