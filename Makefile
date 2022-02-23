# Makefile used to execute some commands locally

env:
	pip3 install -r requirements/develop.txt
	pre-commit install


lint:
	pre-commit run --all-files


watch-lint:
	ptw --runner "pre-commit run -a"


test:
	pytest tests -s


watch:
	ptw --runner "pytest tests -s"


isort:
	isort .


black:
	black . -l 79


flake8:
	flake8 .


pydocstyle:
	pydocstyle --match-dir='(?!test|project).*'


doc:
	export PYTHONPATH=`pwd`:${PYTHONPATH}; \
	cd docs && make html; \
	cd ..


clean-doc:
	cd docs && make clean; \
	cd ..


wheel:
	python3 setup.py sdist bdist_wheel; \
	ls dist


clean-wheel:
	rm -rf dist
