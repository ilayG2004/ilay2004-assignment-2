# Define variables for Python virtual environment and Node.js
PYTHON_ENV = api/venv
PYTHON = $(PYTHON_ENV)/bin/python
PIP = $(PYTHON_ENV)/bin/pip
NPM = npm

# If on Windows, use 'Scripts' instead of 'bin'
ifeq ($(OS),Windows_NT)
  PYTHON = $(PYTHON_ENV)/Scripts/python
  PIP = $(PYTHON_ENV)/Scripts/pip
endif

# Default command to install all dependencies
.PHONY: all install
all: install

# Install all dependencies (backend and frontend)
install: install-backend install-frontend

# Backend setup - Create virtual environment and install dependencies
.PHONY: install-backend
install-backend:
	# Create a Python virtual environment if it doesn't exist (cross-platform)
	@if [ ! -d "$(PYTHON_ENV)" ]; then \
		echo "Creating virtual environment..."; \
		cd api && python3 -m venv venv; \
	fi
	@echo "Upgrading pip..."; \
	$(PIP) install --upgrade pip; \
	@echo "Installing requirements..."; \
	$(PIP) install -r api/requirements.txt

# Frontend setup - Install Node.js dependencies
.PHONY: install-frontend
install-frontend:
	@if [ -d "src" ]; then \
		cd src && $(NPM) install; \
	else \
		echo "src directory not found! Please ensure it exists."; \
		exit 1; \
	fi

# Run the backend Flask app
.PHONY: run-backend
run-backend:
	cd api && $(PYTHON) main.py

# Run the frontend app (assuming a React app)
.PHONY: run-frontend
run-frontend:
	cd src && $(NPM) start

# Clean up virtual environment and node_modules
.PHONY: clean
clean:
	rm -rf $(PYTHON_ENV) src/node_modules
