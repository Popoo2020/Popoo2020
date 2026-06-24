.PHONY: test report validate

test:
	python -m unittest discover -s tests -p 'test_*.py'

report:
	python src/generate_readiness_report.py
	test -f reports/generated_readiness_report.md
	grep -q "AI Governance Readiness Report" reports/generated_readiness_report.md
	grep -q "High-risk use cases" reports/generated_readiness_report.md
	grep -q "Controls requiring follow-up" reports/generated_readiness_report.md

validate: test report
