HUGO ?= hugo

.PHONY: serve build validate lint fmt clean

serve:
	$(HUGO) serve --buildDrafts --disableFastRender

build:
	$(HUGO) --minify

validate:
	python3 scripts/validate_content.py

lint: build
	htmlproofer public/ --disable-external --ignore-missing-alt --allow-hash-href --no-enforce-https

fmt:
	$(HUGO) --minify 2>/dev/null; true

clean:
	rm -rf public/ resources/
