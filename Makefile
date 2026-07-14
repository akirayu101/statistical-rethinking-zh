.PHONY: build audit audit-second-pass audit-third-pass preview extract-chapter-01

build:
	python3 scripts/build_site.py

audit: build
	python3 scripts/audit_site.py

audit-second-pass:
	python3 scripts/audit_second_pass.py

audit-third-pass:
	python3 scripts/audit_third_pass.py

preview: build
	python3 -m http.server 8877 --directory site

extract-chapter-01:
	python3 scripts/extract_source.py --chapter chapter-01
