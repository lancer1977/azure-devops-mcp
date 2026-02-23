.PHONY: run test docker

run:
	python -m app.main

test:
	pytest -q

docker:
	docker build -t ado-mcp:local .
