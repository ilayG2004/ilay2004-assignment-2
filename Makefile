# Define variables for Python virtual environment and Node.js
PYTHON_ENV = api/venv
PYTHON = $(PYTHON_ENV)/bin/python  # Unix-compatible path
PIP = $(PYTHON_ENV)/bin/pip        # Unix-compatible path
NPM = npm

# Default command to install all dependencies
.PHONY: all
all: install-backend install-frontend

# Backend setup - Create virtual environment and install dependencies
.PHONY: install-backend
install-backend:
	# Create a Python virtual environment if it doesn't exist (cross-platform)
	if [ ! -d "$(PYTHON_ENV)" ]; then \
		cd api && python3 -m venv venv && \
		$(PIP) install --upgrade pip && \
		$(PIP) install -r requirements.txt; \
	fi

# Frontend setup - Install Node.js dependencies
.PHONY: install-frontend
install-frontend:
	cd frontend && $(NPM) install

# Run the backend Flask app
.PHONY: run-backend
run-backend:
	cd api && $(PYTHON) main.py

# Run the frontend app (assuming a React app)
.PHONY: run-frontend
run-frontend:
	cd frontend && $(NPM) start

# Clean up virtual environment and node_modules
.PHONY: clean
clean:
	rm -rf $(PYTHON_ENV) frontend/node_modules
