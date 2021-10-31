.PHONY: test clean

test:
	pytest -v tests

clean:
	find . -name ".pytest_cache" | xargs rm -fr
	find . -name "__pycache__" | xargs rm -fr
