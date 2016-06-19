.PHONY: init test doc lint

init:
	pip install -r requirements.txt

test:
	nosetests

doc:
	 sphinx-build -b html . ./_build

lint:
	mypy --silent-imports kokbok/
	flake8 kokbok/
