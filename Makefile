# Makefile

# Specify the Python version
PYTHON_VERSION := python3.11
LAMBDA_VENV := lambda/.lambda_venv
CDK_VENV := .cdk_venv
PACKAGE_NAME := lambda/lambda_package.zip
LAMBDA_FUNCTION := lambda_function.py # Add other files separated by spaces if necessary
CDK_APP_DIR := cdk # Specify the directory of your CDK app

# Default target executed when no arguments are given to make.
default: package cdk_venv cdk_bootstrap cdk_deploy

# Setup a virtual environment
venv:
	$(PYTHON_VERSION) -m venv $(LAMBDA_VENV)
	$(LAMBDA_VENV)/bin/pip install -U pip

cdk_venv:
	$(PYTHON_VERSION) -m venv $(LAMBDA_VENV)
	$(PYTHON_VERSION) -m pip install -r cdk/requirements.txt

# Install dependencies into the virtual environment
dependencies: venv
	$(LAMBDA_VENV)/bin/pip install -r lambda/requirements.txt

# Package the virtual environment libraries and your lambda function into a zip
package: dependencies
	# Adding python packages
	cd $(LAMBDA_VENV)/lib/$(PYTHON_VERSION)/site-packages; zip -r9 $(CURDIR)/$(PACKAGE_NAME) .
	# Adding your lambda function and any additional files
	zip -g $(PACKAGE_NAME) lambda/$(LAMBDA_FUNCTION)

# Bootstrap the CDK (only needs to be run once per AWS account/region)
cdk_bootstrap:
	cd $(CDK_APP_DIR) && cdk bootstrap

# Deploy the CDK stack
cdk_deploy:
	cd $(CDK_APP_DIR) && cdk deploy

# Clean up the environment
clean:
	rm -rf $(LAMBDA_VENV)
	rm -rf $(CDK_VENV)
	rm -f $(PACKAGE_NAME)

.PHONY: default venv dependencies package cdk_venv cdk_bootstrap cdk_deploy clean
