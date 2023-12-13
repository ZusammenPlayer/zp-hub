# zp-hub backend

Manages devices via socketio and provides http api for the frontend.

## setup project

- python 3.10 or higher
- clone repository and cd into it
- create a virtual environment: `python -m venv .venv`
- load virtual environment: `source .venv/bin/activate`
- install depedencies: `pip install -r requirements.txt`
- copy `src/config.template.py` to `src/config.py`
- edit `src/config.py` and change config values to your needs
- go to folder `src` and start the server with: `python app.py`
