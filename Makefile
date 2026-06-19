.PHONY: test benchmark rag-eval security-test full-validation

test:
	pytest tests/unit -m unit

benchmark:
	pytest tests/benchmarks -m benchmark

rag-eval:
	pytest tests/retrieval -m rag

security-test:
	pytest tests/security -m security

full-validation:
	python tests/run_full_pipeline_validation.py
