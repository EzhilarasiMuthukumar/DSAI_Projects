.PHONY: setup data run test clean

# Setup virtual environment and install dependencies
setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt
	@echo "\n✅ Setup complete. Run: source .venv/bin/activate"

# Process raw data into training/test splits
data:
	python scripts/prepare_data.py

# Launch the ADK Web UI
run:
	cd agent && adk web

# Run smoke test
test:
	python scripts/test_agent.py

# Clean generated data and cache
clean:
	rm -rf data/training_data/*
	rm -rf data/test_data/*
	rm -rf __pycache__ agent/__pycache__ agent/spin_coach/__pycache__
	@echo "✅ Cleaned generated data and caches"

# Full setup: install + prepare data + launch
all: setup data run
