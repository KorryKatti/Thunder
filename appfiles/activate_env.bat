@echo off
call myenv\Scripts\activate.bat
pip install -r requirements.txt
python index.py
