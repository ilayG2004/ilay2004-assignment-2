# Define variables for Python virtual environment and Node.js
PYTHON_ENV = api/venv
PYTHON = $(PYTHON_ENV)/Scripts/python
PIP = $(PYTHON_ENV)/Scripts/pip
NPM = npm

# Default command to install all dependencies
.PHONY: all
all: install-backend install-frontend

# Backend setup - Create virtual environment and install dependencies
.PHONY: install-backend
install-backend:
	# Create a Python virtual environment if it doesn't exist
	if not exist $(PYTHON_ENV) ( \
		cd api && python -m venv venv && \
		Set-ExecutionPolicy Unrestricted -Scope Process && \
		$(PIP) install -r api/requirements.txt \
	)

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
