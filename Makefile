venv-setup:
	python -m venv venv

venv-activate:
	source venv/bin/activate

venv-deactivate:
	deactivate

install:
	pip install -r requirements.txt

start:
	python main.py

freeze:
	pip freeze > requirements.txt
