.PHONY: tag local-docs

tag:
	./scripts/tag

local-docs:
	uv run --extra docs mkdocs serve
