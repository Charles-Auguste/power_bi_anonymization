clean:
	@rm -f */version.txt .coverage
	@find . -name '__pycache__' |xargs rm -fr {} \;
	@rm -fr build dist .eggs .pytest_cache
	@rm -fr powerbi_anonymisation_pkg-*.dist-info
	@rm -fr powerbi_anonymisation_pkg.egg-info

# Development workflow

dev_install:
	@python -m pip install --upgrade pip
	@pip3 install -e .
	@git config --local --unset core.hooksPath | true
	@git config --global --unset core.hooksPath | true
	@pre-commit install
	@../.git/hooks/pre-commit

test:
	@py.test -v --cov-report=xml:../ci/pkg_coverage.xml --cov-report term --cov powerbi_anonymisation_pkg

doctest:
	PY_IGNORE_IMPORTMISMATCH=1 \
      py.test -vv --doctest-modules --doctest-glob 'powerbi_anonymisation_pkg/**/*.py' --ignore-glob 'powerbi_anonymisation_pkg/**/*_test.py'

# QA
qa_lines_count:
	@find ./ -name '*.py' -exec  wc -l {} \; | sort -n| awk \
        '{printf "%4s %s\n", $$1, $$2}{s+=$$0}END{print s}'
	@echo ''

qa_check_code:
	@flake8 .

format_code:
	@black .

# Production deploy tools ( Used by CI )
#
install: clean wheel
	@pip3 install -U dist/*.whl --cache-dir /pip_cache

wheel: clean
	@python3 -m build --wheel

run:
	@streamlit run powerbi_anonymisation_pkg/streamlit_powerbi.py

