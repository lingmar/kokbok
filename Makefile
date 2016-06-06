init:
	pip install -r requirements.txt

test:
	nosetests

doc:
	 sphinx-build -b html . ./_build
