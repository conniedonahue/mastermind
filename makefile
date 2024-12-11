### In your terminal, run `make {shortcut}` to run these commands (e.g. `make dev`) ###

# Runs the server in dev
dev:
	FLASK_ENV=development FLASK_APP=run.py flask run

prod:
	FLASK_ENV=production FLASK_APP=run.py gunicorn --bind 0.0.0.0:8000 run:app

# Clears the app.log file
clear-log:
	@echo "" > app.log