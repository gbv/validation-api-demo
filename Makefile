deps:
	[ -d .venv ] || python3 -m venv .venv
	.venv/bin/pip3 install -r requirements.txt
	.venv/bin/pip3 install -r requirements-dev.txt

.PHONY: test doc

test:
	@. .venv/bin/activate && coverage run --branch -m pytest -v -s && coverage report -m

all: # TODO: include integration test with backends
	@. .venv/bin/activate && coverage run --branch -m pytest -v -s && coverage report -m && coverage html

doc:
	rm -rf docs
	.venv/bin/pdoc -o docs lib
start:
	@test -d files || mkdir files
	@.venv/bin/python3 app.py

lint:
	@.venv/bin/flake8 *.py lib/ tests/ --ignore=C901,E741,W504 --exit-zero --max-complexity=10 --max-line-length=100 --statistics

fix:
	@.venv/bin/autopep8 --in-place --max-line-length=100 *.py lib/*.py lib/*/*.py tests/*.py

loc:
	cloc $$(git ls-files)


