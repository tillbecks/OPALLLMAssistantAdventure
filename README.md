# OPALLLMAssistantAdventure
This project aims to create a function calling LLM as an intermediator between users an the static analysis framework OPAL

# Installation

# Setting up a Python Environment for `functionCallingCode.py`

This guide explains how to set up a Python virtual environment, install the required dependencies, and configure the script `functionCallingCode.py`.

## 1. Create a Virtual Environment

A virtual environment allows you to manage project-specific dependencies independently of your system-wide Python packages.

```bash
# Create a virtual environment named 'venv'
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

Once activated, your terminal prompt should display the name of the virtual environment, e.g., (venv).

## 2. Install Required Python Packages

With the virtual environment activated, install the groq and subprocess packages:

```bash
pip install groq subprocess
```

Note: If pip is not up to date, you can update it by running:

```bash
python -m pip install --upgrade pip
```

## 3. Configure functionCallingCode.py

The script functionCallingCode.py requires two variables to be configured:

    secret_value: Set this to your API key.
    PATH_OPAL: Set this to the path of your OPAL directory.

Example Configuration

Open functionCallingCode.py in a text editor, and update the variables as follows:

# Replace 'your_api_key_here' with your actual API key
secret_value = 'your_api_key_here'

# Replace 'your_opal_directory_path' with the absolute path to your OPAL directory
PATH_OPAL = 'your_opal_directory_path'

Tips for Setting the Path

- On Windows, ensure the path uses double backslashes `\\` or forward slashes `/`, e.g., `C:\\Users\\YourUser\\OPAL` or `C:/Users/YourUser/OPAL`.
- On macOS/Linux, you can use the standard forward slash `/`, e.g., `/home/youruser/opal`.

4. Run the Script

After completing the setup:
```bash
# Ensure the virtual environment is activated
python functionCallingCode.py
```

You should now have the script running with the correct dependencies and configuration.
