.PHONY: check build test a11y pages check-pages pages-test pages-a11y
.NOTPARALLEL:
PYTHON ?= python
EVIDENCE ?= $(CURDIR)/qa-reports
export OWA_EVIDENCE := $(EVIDENCE)

check: a11y

build:
	$(PYTHON) build.py

test: build
	$(PYTHON) -m py_compile build.py verify.py test_verify.py pages.py test_pages.py
	node --check source/theme.js
	node --check browser-qa.mjs
	$(PYTHON) -m unittest -v test_verify test_pages
	$(PYTHON) verify.py --report "$(EVIDENCE)/content-verification.json"
	git diff --check

a11y: test
	mkdir -p "$(EVIDENCE)"
	cp test-assets/axe.min.js "$(EVIDENCE)/axe.min.js"
	node browser-qa.mjs
	node browser-qa.mjs --dark
	node browser-qa.mjs --no-js
	node browser-qa.mjs --no-js --dark

# No GitHub repository or credentials are needed for these local targets.
PAGES_ARGS ?=
pages:
	$(PYTHON) pages.py $(PAGES_ARGS)

pages-test: test pages
	$(PYTHON) pages.py --verify-only

check-pages: pages-a11y

pages-a11y: pages-test
	node browser-qa.mjs --pages
	node browser-qa.mjs --pages --dark
	node browser-qa.mjs --pages --no-js
	node browser-qa.mjs --pages --no-js --dark
