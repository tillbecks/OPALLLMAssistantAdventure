# OPALLLMAssistantAdventure
This project aims to create a function-calling LLM as an intermediator between users and the static analysis framework OPAL. We dearly call it "OpalGPT", despite not using GPT models. In the LLMs own words: 
> "I am a Java bytecode analysis tool that utilizes the Opal framework to conduct various analyses on Java bytecode." - OpalGPT


# Installation

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

## 2. Install Dependencies

With the virtual environment activated, install the groq package:

```bash
pip install groq
```

Note: If pip is not up to date, you can update it by running:

```bash
python -m pip install --upgrade pip
```

Lastly, clone the [OPAL project](https://github.com/opalj/opal/tree/develop) into your machine.

## 3. Configure functionCallingCode.py and secret_keys.py

### secret_keys.py
The repository contains a file `secret_keys_template.py`. You have to copy this file and rename it to `secret_keys.py`, then insert your own secret keys:

```python
CROQ_SECRET_API_KEY = "Insert your secret croq key"
PATH_OPAL = "Insert your path to Opal here"
PATH_DECOMPILER = "Insert your path to the cfr.jar here"
STD_LOG_PATH = "log.txt"
```

The `PATH_DECOMPILER` variable specifies the path to the decompiler required in step 2, and `STD_LOG_PATH` defines the standard file name for logging.

## 4. Install and Configure the Decompiler

We have installed a decompiler from [this link](https://www.benf.org/other/cfr/). It is called CFR and allows our LLM to disassemble Java bytecode. Users must download the decompiler JAR file and set the `PATH_DECOMPILER` variable in the configuration file accordingly.

## 5. Running the Program

Once everything is set up, you can start the program by running:

```bash
python functionCallingCode.py
```

This will launch the LLM-based interface, allowing you to interact with OPAL through function calls.

# Overview of Available Functions

The LLM can call the following functions:

- `get_response`: Responds to casual chat messages.
- `list_functions`: Returns a JSON listing all callable functions and their parameters.
- `string_constants_analysis`: Analyzes Java bytecode for hardcoded string values.
- `field_assignability_analysis`: Determines whether fields can be modified after initialization.
- `field_immutability_analysis`: Checks if fields remain unchanged after initialization.
- `bytecode_disassembler`: Disassembles Java bytecode and optionally saves the output.
- `hierarchy_visualisation`: Generates a `.gv` visualization file of a JAR’s hierarchy.
- `field_array_usage_analysis`: Analyzes how arrays stored as fields are accessed and modified.
- `local_points_to`: Tracks memory references of local variables in a program.
- `print_tac`: Prints the three-address code representation of a Java method.
- `parameter_usage_analysis`: Examines how method parameters are used or modified.
- `suggest_analysis`: Suggests relevant OPAL analysis techniques for a given `.class` file.
- `taint_analysis`: Tracks untrusted data flow from sources to sinks to detect vulnerabilities.
- `decompile_and_analyze_or_print`: Decompiles Java bytecode and prints or analyzes it based on the user's request.

This set of functions enables comprehensive analysis and manipulation of Java bytecode with OPAL and the LLM acting as an intermediary.

# How to use each funtion

For each OPAL analysis, these are the inputs you should give to the LLM:

- `string_constants_analysis`: a file path to the Java bytecode file (.class file).
- `field_assignability_analysis`: a file path to the Java bytecode file (.class file).
- `field_immutability_analysis`: a file path to the Java bytecode file (.class file).
- `bytecode_disassembler`:
   - a file path to the Java bytecode file (.class file)
   - (optional) a safe path to store the disassembled file
   - (optional) a name for the disassembled file
- `hierarchy_visualisation`:
   - a file path to the jar file
   - (optional) a safe path to store the .gv file
- `field_array_usage_analysis`: a file path to the class or jar file.
- `local_points_to`:
   - a file path to the class or jar file
   - a method name
- `print_tac`:
   - a file path to the class or jar file
   - a method name
- `parameter_usage_analysis`: a file path to the Java bytecode file.
- `suggest_analysis`: a file path to the .class file.
- `taint_analysis`:
    - a source method
    - a source parameter
    - a folder containing files
    - a sink method
- `decompile_and_analyze_or_print`:
    - a file path to the class or jar file
    - (optional) the directory in which the java class files are stored

# Our experiments

## The Language Model

We tried many different LLMs available for free at Groq for our project, namely:

- llama-3.3-70b-versatile
- llama3-70b-8192 
- deepseek-r1-distil-llama-70b
- llama-3.2-90b-vision-preview

Some of them gave unsatisfying answers, hallucinated too much or just didn't seem to reason well enough for our purposes. Another issue we ran into was the token limits of the Groq API. We needed a model that could reason well, but at the same time allow us to send a reasonable amount of tokens per minute. We finally settled down with `llama-3.3-70b-versatile` and set it's temperature (how creative the model is allowed to be) for 0.2, to avoid hallucinations but allow for some creativity.

## Code Analysis 

One of our goals was to have the LLM help the user decide what OPAL analysis to run on the target code. For this purpose we thought of two approaches:

### Disassembler based

The function `suggest_analysis` is a rule-based suggestion tool that uses the `javap` disassembler to analyse the code. The disassembler outputs bytecode instructions (opcodes). We then count the ocurences of key opcodes and if those surpass a certain threshold, suggest a fitting analysis. We don't take the lenght of the document into account, which could be a problem, given long documents will almost certainly surpass all thresholds. There is a lot of room for improvement in this funcion. Because it is a quite simplistic approach, and we didn't dwell too long on it, as the next approach proved itself to be a lot better. 

### Decompiler based

In order for the LLM to be able to analyse our code and suggest OPAL analysis based on that, it's own prior knowldge and our descriptions of the available functions, we used a decompiling function. The decompiler we choose for this is `cfr`. This approach was so good :) blablablabll write more

## Memory System

Since the Groq API does not provide memory for LLMs, we have implemented a memory mechanism that retains conversation history. This is managed using the following class:

```python
import datetime
import json

class Memory:
    def __init__(self, max_size=30):
        self.memory = []
        self.max_size = max_size

    def get(self, newest_count=-1):
        if newest_count > len(self.memory) or newest_count < 0:
            newest_count = len(self.memory)
        return self.memory[:newest_count]
    
    def get_json_textual(self, newest_count=-1):
        content = ""
        if newest_count > len(self.memory) or newest_count < 0:
            newest_count = len(self.memory)
        for i in reversed(range(newest_count)):
            content += self.memory[i]["type"] + ": " + self.memory[i]["content"] + "\n"
        return content

    def insert(self, arg_type, content):
        self.memory.insert(0, {"type": arg_type, "content": content})
        if len(self.memory) > self.max_size:
            self.memory.pop()
```

## Logging System

A logging mechanism has been added in `logger.py`, which records both user conversations and the functions executed by the LLM, including the parameters used. The log file is defined in the configuration file (`STD_LOG_PATH`) and defaults to `log.txt`. The log file resets upon restarting the program.

## Problems

- **Token Limits**: In order to mitigate this issue, we trim the output of OPAL, which could make the results less accurate. Further down the road, we decided to upgrade our Groq subscription. The project also works on the basic tier, although the user could face problems when the API reaches it's limit.
- **LLM Misbehavior**: Sometimes the LLM makes up information (hallucinates) or doesn't follow instructions perfectly. That doesn't happen so often, and if it happens, restarting the chat can be a solution. 








