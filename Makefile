.PHONY: install lint test dry-run deck publish ci

install:
	python -m pip install -e ".[dev]"

lint:
	ruff check .

test:
	pytest

dry-run:
	threads-auto-poster publish --file examples/posts/sample_posts.txt --dry-run --output dist/publish-result.json

deck:
	python scripts/build_keynote_deck.py --output dist/keynote/threads-auto-poster-keynote.pptx

publish:
	threads-auto-poster publish --file content/post_queue.txt --execute --output dist/publish-result.json

ci: lint test deck
