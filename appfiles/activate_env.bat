@echo off
call myenv\Scripts\activate.bat
call pip install -r requirements.txt
call python index.py
