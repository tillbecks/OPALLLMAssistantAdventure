import subprocess
import json
import os
from secret_keys import PATH_OPAL
from decompilerModule import decompile_no_write
from logger import log

all_function_list = []

#Just a helper funtion to run sbt commands in the opal directory specified by the user. 
def  run_sbt_command(command):
    # Format the command as a single string
    full_command = f'sbt "{command}"'

    log("About to execute the following command: ", full_command)
    
    try:
        result = subprocess.run(
            full_command,
            cwd=PATH_OPAL,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        result = result.stdout.split("[info] [info][project]")[-1]
        log("The execution was succesful and resulted in the following output: ", result)
        return result
    except FileNotFoundError as e:
        error_msg = "";
        error_msg += f"SBT not found in PATH. Error: {e}\n"
        error_msg += f"Current PATH: {os.environ.get('PATH', '')}"
        log("The execution wasn't succesful and resulted in the following error: ", error_msg)
        raise e
    except subprocess.CalledProcessError as e:
        error_msg = ""
        error_msg += f"Command failed with error: {e}"
        error_msg += f"Error output: {e.stderr}"
        log("The execution wasn't succesful and resulted in the following error: ", error_msg)
        raise e
#In the following, all available functions are defined. Based on the Information in this list, the LLM makes a decision which function to call.

#A Function to responde to a casual chat
def get_response(question):
    log("Call of function 'get_response' with the following question: ", question)
    return json.dumps({"question": question})

get_response_obj = {
    "function": get_response,
    "definition":{
        "type": "function",
        "function": {
            "name": "get_response",
            "description": "Responding a casual chat",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The the content of the question the user asked or the statement the user made. (e.g. 'Hello, how are you?')" ,
                    }
                },
                "required": ["question"],
            },
        },
    }
}
all_function_list.append(get_response_obj)

#A Function that lists all available functions
def list_functions():
    response = ""
    for tool in all_function_list:
        response += tool["definition"]["function"]["name"] + ": " + tool["definition"]["function"]["description"] + "\n"
    log("Call of function 'list_functions' with the following output: ", response)
    return json.dumps({"reply": "You are able to use the following functions: " + response})

list_functions_obj = {
    "function": list_functions,
    "definition":    {
        "type": "function",
        "function": {
            "name": "list_functions",
            "description": "Returns the json containing all of your callable functions, what they do and what parameters they use. Use this function to retrieve information about available capabilities or needed parameters instead of directly calling other functions." + 
            "e.g. 'Please list all functions' or 'What parameters does the function  xy need?'",
        },
    }
}
all_function_list.append(list_functions_obj)

#This function conducts a string constants analysis on the java bytecode specified in the file path.
def string_constants_analysis(file_path):
    normalized_path = os.path.normpath(file_path)
    log("Call of function 'string_constants_analysis' with the following file path (already normalized): ", normalized_path)

    if not os.path.exists(normalized_path):
        error_message = f"Error: File does not exist at path: {normalized_path}"
        log("The execution wasn't succesful and resulted in the following error: ", error_message)
        return json.dumps({"reply": error_message})
    
    sbt_command = "project Tools; runMain org.opalj.support.info.StringConstants -cp=" + normalized_path
    try:
        answer = run_sbt_command(sbt_command)
    except subprocess.CalledProcessError as e:
        log("The execution wasn't succesful and resulted in the following error: ", str(e))
        return json.dumps({"reply": "The following error occured: " + str(e)})
    except FileNotFoundError:
        log("The execution wasn't succesful and resulted in the following error: FileNotFoundError")
        return json.dumps({"reply": "FileNotFoundError"})
    

    log("The execution was succesful and resulted in the following output: ", answer)
    return json.dumps({"reply": answer})

string_constants_analysis_obj = {
    "function": string_constants_analysis,
    "definition": { 
        "type": "function",
        "function":{
            "name": "string_constants_analysis",
            "description": "Uses Opal to conduct a string constants analysis on the java bytecode specified in a file path. Here is a little description what a string constants analysis does: String constants analysis identifies and examines hardcoded string values in a program. It helps detect sensitive information (e.g., passwords, API keys) or potential issues like hardcoded configuration values. The analysis focuses on how these strings are used, ensuring they are managed securely and adhere to best practices, such as avoiding hardcoded secrets or enabling localization for user-facing text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path":{
                        "type":"string",
                        "description":"path to the class-file containing the java bytecode to be analysed (e.g. '/usr/home/filename.class')"
                    }
                },
                "required": ["file_path"],
            },
        },
    }
}
all_function_list.append(string_constants_analysis_obj)

#This function conducts a field assignability analysis on the java bytecode specified in the file path.
def field_assignability_analysis(file_path):
    normalized_path = os.path.normpath(file_path)
    log("Call of function 'field_assignability_analysis' with the following file path (normalized): ", normalized_path)

    if not os.path.exists(normalized_path):
        log("The execution wasn't succesful and resulted in the following error: File does not exist at path: ", normalized_path)
        return json.dumps({"reply": f"Error: File does not exist at path: {normalized_path}"})

    sbt_command = "project Demos; runMain org.opalj.fpcf.analyses.FieldAssignabilityAnalysisDemo -cp=" + normalized_path 
    try:
        answer = run_sbt_command(sbt_command)
    except subprocess.CalledProcessError as e:
        log("The execution wasn't succesful and resulted in the following error: ", str(e))
        return json.dumps({"reply": "The following error occured: " + str(e)})
    except FileNotFoundError:
        log("The execution wasn't succesful and resulted in the following error: File does not exist at path: ", normalized_path)
        return json.dumps({"reply": "FileNotFoundError"})
    

    log("The execution wasn succesful and resulted in the following output: ", answer)
    return json.dumps({"reply": answer}) 

field_assignability_analysis_obj = {
    "function": field_assignability_analysis,
    "definition": {
        "type": "function",
        "function":{
            "name": "field_assignability_analysis",
            "description": "Conducts a field assignability analysis on the java bytecode specified in the file path. Here is a little description of a field assignability analysis: Field assignability analysis determines whether fields (variables or properties) in a program can be modified after initialization. It identifies fields marked as read-only, immutable, or constant, ensuring they are not improperly reassigned. This analysis helps enforce design constraints, improve code safety, and prevent unintended side effects caused by unauthorized modifications.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path":{
                        "type":"string",
                        "description":"path to the class-file containing the java bytecode to be analysed (e.g. '/usr/home/filename.class')"
                    }
                },
                "required": ["file_path"],
            },
        },
    }
}
all_function_list.append(field_assignability_analysis_obj)
    
#This function conducts a field immutability analysis on the java bytecode specified in the file path.
def field_immutability_analysis(file_path):
    normalized_path = os.path.normpath(file_path)
    log("Call of function 'field_immutability_analysis' with the following file path (normalized): ", normalized_path)

    if not os.path.exists(normalized_path):
        log("The execution wasn't succesful and resulted in the following error: File does not exist at path: ", normalized_path)
        return json.dumps({"reply": f"Error: File does not exist at path: {normalized_path}"})
    
    sbt_command = "project Demos; runMain org.opalj.fpcf.analyses.FieldImmutabilityAnalysisDemo -cp=" + normalized_path 
    try:
        answer = run_sbt_command(sbt_command)
    except subprocess.CalledProcessError as e:
        log("The execution wasn't succesful and resulted in the following error: ", str(e))
        return json.dumps({"reply": "The following error occured: " + str(e)})
    except FileNotFoundError:
        log("The execution wasn't succesful and resulted in the following error: File does not exist at path: ", normalized_path)
        return json.dumps({"reply": "FileNotFoundError"})
    
    log("The execution was succesful and resulted in the following output: ", answer)
    return json.dumps({"reply": answer})

field_immutability_analysis_obj = {
    "function": field_immutability_analysis,
    "definition":{
        "type": "function",
        "function":{
            "name": "field_immutability_analysis",
            "description": "conduct a field immutability analysis on the java bytecode specified in the file path. Here is a short explanation: Field immutability analysis identifies fields in a program that are intended to remain unchanged after initialization. It ensures that these fields, often marked as immutable or read-only, are not modified during runtime. This analysis helps enforce design principles, improve thread safety, and prevent unintended side effects by guaranteeing that critical data remains constant throughout the program’s execution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path":{
                        "type":"string",
                        "description":"path to the class-file containing the java bytecode to be analysed (e.g. '/usr/home/filename.class')"
                    }
                },
                "required": ["file_path"],
            },
        },
    }
}
all_function_list.append(field_immutability_analysis_obj)   

#This function creates a html file, that visualizes the disassembled bytecode of a class file. The file is stored in the safe_path if specified, otherwise in the same directory as the class file.
def bytecode_disassembler(file_path, safe_path, disassembled_file_name=""):
    normalized_path = os.path.normpath(file_path)
    normalized_safe_path = os.path.normpath(safe_path)

    log("Call of function 'bytecode_disassembler' with the following file path (normalized) and safe path (normalized): ", normalized_path, normalized_safe_path)

    if not os.path.exists(normalized_path):
        log("The execution wasn't succesful and resulted in the following error: File does not exist at path: ", normalized_path)
        return json.dumps({"reply": f"Error: File does not exist at path: {normalized_path}"})

    try:
        sbt_command = "project BytecodeDisassembler; run -source " + normalized_path

        if disassembled_file_name:
            disassembled_file_name = disassembled_file_name.split(".")[0]
            safe_file = os.path.join(normalized_safe_path, disassembled_file_name + ".html")
        else:
            file_name = normalized_path.split("/")[-1].split(".")[0]
            safe_file = os.path.join(normalized_safe_path, file_name + ".html")

        sbt_command += " -o " + safe_file

        answer = run_sbt_command(sbt_command)

        log("The execution was succesful and resulted in the following output: ", answer)
        return json.dumps({"reply": answer})

    except subprocess.CalledProcessError as e:
        log("The execution wasn't succesful and resulted in the following error: ", str(e))
        return json.dumps({"reply": "The following error occured: " + str(e)})
    except FileNotFoundError: 
        log("The execution wasn't succesful and resulted in the following error: FileNotFoundError")
        return json.dumps({"reply": "FileNotFoundError"})
    except PermissionError:
        log("The execution wasn't succesful and resulted in the following error: PermissionError")
        return json.dumps({"reply": "PermissionError while trying to write the disassembled file to the specified path."})

bytecode_disassembler_obj = {
    "function": bytecode_disassembler,
    "definition": {
        "type": "function",
        "function": {
            "name": "bytecode_disassembler",
            "description": "Dissasembles the java bytecode specfied in the file path. If the user also specifies a safe path, the disassembled file will be stored there, otherwise just uses the same directory in which the class file is saved in. If they also specify a name for the disassembled file, the disassembled file will be stored with that name, otherwise it will be stored with the name of the original file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "path to the class-file containing the java bytecode to be disassembled (e.g. '/usr/home/filename.class'). This variable can also be the path to a directory which is also okay (e.g. '/usr/home/')."
                    },
                    "safe_path": {
                        "type": "string",
                        "description": "path to the directory where the disassembled files should be stored (e.g. '/usr/home/')"
                    },
                    "disassembled_file_name": {
                        "type": "string",
                        "description": "name of the disassembled file (e.g. 'disassembled_file' or 'dissaembled_file.html')"
                    },
                },
                #Es muss ein safe_path angegeben werden, da der output der Funktion zu groß wäre um Ihn an das LLM zu senden.
                "required": ["file_path", "safe_path"],
            },
        },
    }
}
all_function_list.append(bytecode_disassembler_obj)


def hierarchy_visualisation(file_path):
    normalized_path = os.path.normpath(file_path)
    log("Call of function 'hierarchy_visualisation' with the following file path (normalized): ", normalized_path)

    if not os.path.exists(normalized_path):
        log("The execution wasn't succesful and resulted in the following error: File does not exist at path: ", normalized_path)
        return json.dumps({"reply": f"Error: File does not exist at path: {normalized_path}"})

    try:
        sbt_command = "project Tools; runMain org.opalj.support.debug.ClassHierarchyVisualizer " + normalized_path
        answer = run_sbt_command(sbt_command)
        return_message = ""
        return_message += answer
        log("The execution was succesful and resulted in the following output: ", return_message)
        return json.dumps({"reply": return_message})
    except subprocess.CalledProcessError as e:
        log("The execution wasn't succesful and resulted in the following error: ", str(e))
        return json.dumps({"reply": "The following error occured: " + str(e)})
    

hierarchy_visualisation_obj = {
    "function": hierarchy_visualisation,
    "definition":{
        "type": "function",
        "function": {
            "name": "hierarchy_visualisation",
            "description": "Uses opal to generate a .gv file that contains a visualization of a specified jar in the file path. If the user also specifies a safe path, the generated file will be stored there. Otherwise the file will be saved in the file specified by its response." ,
            #"description": "Visualize the class hierarchy of the jar specified in the file path. If the user also specifies a safe path, the generated file will be stored there, otherwise just let the safe_path as empty string. In this case the file will be saved in the file specified by its response.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "path to the jar containing the content to be visualized (e.g. '/usr/home/programm.jar')."
                    },
                },
                "required": ["file_path"],
            },
        },
    }
}
all_function_list.append(hierarchy_visualisation_obj)

#This function conducts a field array usage analysis on the java bytecode specified in the file path.
def field_array_usage_analysis(file_path):
    normalized_path = os.path.normpath(file_path)
    log("Call of function 'field_array_usage_analysis' with the following file path (normalized): ", normalized_path)

    if not os.path.exists(normalized_path):
        log("The execution wasn't succesful and resulted in the following error: File does not exist at path: ", normalized_path)
        return json.dumps({"reply": f"Error: File does not exist at path: {normalized_path}"})

    sbt_command = "project Demos; runMain org.opalj.tac.FieldAndArrayUsageAnalysis -cp=" + normalized_path
    try:
        answer = run_sbt_command(sbt_command)
    except subprocess.CalledProcessError as e:
        log("The execution wasn't succesful and resulted in the following error: ", str(e))
        return json.dumps({"reply": "The following error occured: " + str(e)})
    except FileNotFoundError:
        log("The execution wasn't succesful and resulted in the following error: FileNotFoundError")
        return json.dumps({"reply": "FileNotFoundError"})
    
    log("The execution was succesful and resulted in the following output: ", answer)
    return json.dumps({"reply": answer})

field_array_usage_analysis_obj = {
    "function": field_array_usage_analysis,
    "definition":{
        "type": "function",
        "function": {
            "name": "field_array_usage_analysis",
            "description": "Conducts a field array usage analysis on the java bytecode specified in the class or jar file specified in the path. Here is an explanation: Field array usage analysis examines how arrays stored as fields in a program are accessed, modified, and managed. It identifies patterns such as out-of-bounds access, improper initialization, or inconsistent updates. This analysis helps ensure proper handling of array data, preventing runtime errors like index exceptions and improving overall code reliability and performance.",
            "parameters":
            {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "path to the class-file or jar containing the java bytecode to be analysed (e.g. '/usr/home/filename.class' or '/usr/home/filename.jar')"
                    },
                },
                "required": ["file_path"],
            },
        }
    }
}
all_function_list.append(field_array_usage_analysis_obj)

#This function collects points-to information rel, safe_path=""ated to a method in a specific class or jar file.
def local_points_to(file_path, method=""):

    normalized_path = os.path.normpath(file_path)
    log("Call of function 'local_points_to' with the following file path (normalized) and method: ", normalized_path, method)

    if method == '':
        log("The execution wasn't succesful and resulted in the following error: Method not especified.")
        return json.dumps({"reply": f"Method not especified."})

    if not os.path.exists(normalized_path):
        log("The execution wasn't succesful and resulted in the following error: File does not exist at path: ", normalized_path)
        return json.dumps({"reply": f"Error: File does not exist at path: {normalized_path}"})

    sbt_command = "project Demos; runMain org.opalj.tac.LocalPointsTo "+ normalized_path + " " + method
    try:
        answer = run_sbt_command(sbt_command)
    except subprocess.CalledProcessError as e:
        log("The execution wasn't succesful and resulted in the following error: ", str(e))
        return json.dumps({"reply": "The following error occured: " + str(e)})
    except FileNotFoundError:
        log("The execution wasn't succesful and resulted in the following error: FileNotFoundError")
        return json.dumps({"reply": "FileNotFoundError"})
    
    log("The execution was succesful and resulted in the following output: ", answer)
    return json.dumps({"reply": answer})

local_points_to_obj = {
    "function": local_points_to,
    "definition":{
        "type": "function",
        "function": {
            "name": "local_points_to",
            "description": "Collect points-to information related to a method in a specific class or jar file. Here is a short description: Local points-to analysis tracks the relationships between local variables and the memory locations (objects or addresses) they reference within a program. It determines which objects a variable can point to at any point in the code, helping identify potential issues like null pointer dereferences, memory leaks, or aliasing problems. This analysis is essential for understanding data flow and ensuring memory safety in complex code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "path to the class-file or jar containing the java bytecode to be analysed (e.g. '/usr/home/filename.class' or '/usr/home/filename.jar')"
                    },
                    "method": {
                        "type": "string",
                        "description": "name of the method in the class file to be analysed (e.g. 'main')"
                    }
                },
                "required": ["file_path", "method"],
            }
        }
    }
}
all_function_list.append(local_points_to_obj)

#This function prints the complete three address code representation of a method in a specific class or jar file.
#But the LLM tends to only show the three address code related to the specified function, even though the the opal function returns the tac of the whole class.
def print_tac(file_path, method=""):

    normalized_path = os.path.normpath(file_path)
    log("Call of function 'print_tac' with the following file path (normalized) and method: ", normalized_path, method)

    if method == '':
        log("The execution wasn't succesful and resulted in the following error: Method not especified.")
        return json.dumps({"reply": f"Method not especified."})

    if not os.path.exists(normalized_path):
        log("The execution wasn't succesful and resulted in the following error: File does not exist at path: ", normalized_path)
        return json.dumps({"reply": f"Error: File does not exist at path: {normalized_path}"})
    
    sbt_command = "project Demos; runMain org.opalj.tac.PrintTAC "+ normalized_path + " " + method
    try:
        answer = run_sbt_command(sbt_command)
    except subprocess.CalledProcessError as e:
        log("The execution wasn't succesful and resulted in the following error: ", str(e))
        return json.dumps({"reply": "The following error occured: " + str(e)})
    except FileNotFoundError:
        log("The execution wasn't succesful and resulted in the following error: FileNotFoundError")
        return json.dumps({"reply": "FileNotFoundError"})
    
    log("The execution was succesful and resulted in the following output: ", answer)
    return json.dumps({"reply": answer})

print_tac_obj = {
    "function": print_tac,
    "definition":{
        "type": "function",
        "function": {
            "name": "print_tac",
            "description": "Prints the complete three address code representation of a method in a specific class or jar file. The output can be very long and should be returned in its entirety. This function helps analyze the low-level code structure of Java methods.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "path to the class-file or jar containing the java bytecode to be analysed (e.g. '/usr/home/filename.class' or '/usr/home/filename.jar')"
                    },
                    "method": {
                        "type": "string",
                        "description": "name of the method in the class file to be analysed (e.g. 'main')"
                    }
                },
                "required": ["file_path", "method"],
            }
        },
    }
}
all_function_list.append(print_tac_obj)


#This function conducts a parameter usage analysis on the java bytecode specified in the file path.
def parameter_usage_analysis(file_path):
    normalized_path = os.path.normpath(file_path)

    log("Call of function 'parameter_usage_analysis' with the following file path (normalized): ", normalized_path)

    if not os.path.exists(normalized_path):
        log("The execution wasn't succesful and resulted in the following error: File does not exist at path: ", normalized_path)
        return json.dumps({"reply": f"Error: File does not exist at path: {normalized_path}"})

    sbt_command = "project Demos; runMain org.opalj.ai.domain.l0.ParameterUsageAnalysis -cp=" + normalized_path 
    try:
        answer = run_sbt_command(sbt_command)
    except subprocess.CalledProcessError as e:
        log("The execution wasn't succesful and resulted in the following error: ", str(e))
        return json.dumps({"reply": "The following error occured: " + str(e)})
    except FileNotFoundError:
        log("The execution wasn't succesful and resulted in the following error: FileNotFoundError")
        return json.dumps({"reply": "FileNotFoundError"})
    
    log("The execution was succesful and resulted in the following output: ", answer)
    return json.dumps({"reply": answer})

parameter_usage_analysis_obj = {
    "function": parameter_usage_analysis,
    "definition":{
        "type": "function",
        "function":{
            "name": "parameter_usage_analysis",
            "description": "conduct a parameter usage analysis on the java bytecode specified in the file path. Here is a little explanation: Parameter usage analysis examines how function or method parameters are used within a program. It identifies whether parameters are read, modified, or ignored, and checks for issues like unused parameters, improper modifications, or violations of intended usage constraints. This analysis helps improve code quality, maintainability, and adherence to design contracts by ensuring parameters are used correctly and efficiently.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path":{
                        "type":"string",
                        "description":"path to the class-file containing the java bytecode to be analysed (e.g. '/usr/home/filename.class')"
                    }
                },
                "required": ["file_path"],
            },
        },
    }
}
all_function_list.append(parameter_usage_analysis_obj)

def suggest_analysis(file_path):
    """Suggests a specific OPAL analysis based on bytecode patterns."""
    normalized_path = os.path.normpath(file_path)
    log("Call of function 'suggest_analysis' with the following file path (normalized): ", normalized_path)

    if not os.path.exists(normalized_path):
        log("The execution wasn't succesful and resulted in the following error: File does not exist at path: ", normalized_path)
        return json.dumps({"reply": f"Error: File does not exist at path: {normalized_path}"})

    try:
        # Run `javap` to disassemble the bytecode
        javap_output = subprocess.run(
            ["javap", "-c", normalized_path],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).stdout.lower()

        # Count occurrences of important bytecode instructions
        ldc_count = javap_output.count("ldc")  # String constants
        putfield_count = javap_output.count("putfield")  # Field assignments
        getfield_count = javap_output.count("getfield")
        invokevirtual_count = javap_output.count("invokevirtual")  # Method calls
        array_usage_count = javap_output.count("newarray") + javap_output.count("arraylength")

        # Define analysis recommendations
        suggestions = []

        if ldc_count >= 3:
            suggestions.append("String Constants Analysis (multiple hardcoded strings detected).")

        if putfield_count > 2 or getfield_count > 2:
            suggestions.append("Field Assignability Analysis (significant field usage).")

        if invokevirtual_count > 5:
            suggestions.append("Local Points-To Analysis (frequent method calls detected).")

        if array_usage_count > 1:
            suggestions.append("Field Array Usage Analysis (array manipulations detected).")

        if not suggestions:
            return json.dumps({"reply": "No obvious recommendations. Consider manual selection."})

        log("The execution was succesful and resulted in the following output: ", suggestions)

        return json.dumps({"reply": "Recommended analyses:\n" + "\n".join(suggestions)})

    except subprocess.CalledProcessError:
        log("The execution wasn't succesful and resulted in the following error: Could not inspect bytecode.")
        return json.dumps({"reply": "Error: Could not inspect bytecode."})

suggest_analysis_obj = {
    "function": suggest_analysis,
    "definition":{
        "type": "function",
        "function": {
            "name": "suggest_analysis",
            "description": "Analyzes a .class file to suggest relevant OPAL analysis techniques. This helps users decide which analysis to perform based on the bytecode structure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the .class file to analyze (e.g. '/usr/home/filename.class')."
                    }
                },
                "required": ["file_path"],
            },
        },
    }
    
}

all_function_list.append(suggest_analysis_obj);

#This function conducts a taint analysis on the java bytecode specified in the file path.
def taint_analysis(file_path, source="", sink=""):
    normalized_path = os.path.normpath(file_path);

    log("Call of function 'taint_analysis' with the following file path (normalized) ", file_path, " sources ", source, " sinks ", sink)

    if source == "" or sink == "":
        log("The execution wasn't succesful and resulted in the following error: No source and/or sink was provided.")
        return json.dumps({"reply": "Error: No source and/or sink was provided."});

    if not os.path.exists(normalized_path):
        log("The execution wasn't succesful and resulted in the following error: File does not exist at path: ", normalized_path)
        return json.dumps({"reply": f"Error: File does not exist at path: {normalized_path}"})

    sbt_command = "project Demos; runMain org.opalj.tac.fpcf.analyses.taint.ConfigurableJavaForwardTaintAnalysisRunner \\\"" + normalized_path + "\\\" --sources " + f'\\"{source}\\"' + " --sinks " + f'\\"{sink}\\"'
    try:
        answer = run_sbt_command(sbt_command)
    except subprocess.CalledProcessError as e:
        log("The execution wasn't succesful and resulted in the following error: ", str(e))
        return json.dumps({"reply": "The following error occured: " + str(e)})
    except FileNotFoundError:
        log("The execution wasn't succesful and resulted in the following error: FileNotFoundError")
        return json.dumps({"reply": "FileNotFoundError"})
    
    log("The execution was succesful and resulted in the following output: ", answer)
    return json.dumps({"reply": answer})

taint_analysis_obj = {
    "function": taint_analysis,
    "definition":{
        "type": "function",
        "function": {
            "name": "taint_analysis",
            "description": "Does a taint analysis on files in a folder, analyzing the flow from a source to a sink. Here is a short explanation: Taint analysis tracks untrusted (tainted) data through a program to detect security vulnerabilities. It ensures data is sanitized before reaching sensitive operations. A source is where tainted data enters, such as user input or API parameters. A sink is where tainted data is used unsafely, like in database queries or system commands. The goal is to prevent vulnerabilities like SQL injection or XSS by ensuring tainted data from sources is sanitized before reaching sinks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the folder containing class files to be analyzed (e.g. '/usr/home/code')."
                    },
                    "source": {
                        "type": "string",
                        "description": "The method of the java programm which the analysis should consider as source (e.g. 'java.lang.String testcode.IndirectStringLeak.getMessage()')."
                    },
                    "sink":{
                        "type": "string",
                        "description": "The method of the java programm which the analysis should consider as source (e.g. 'void testcode.IndirectStringLeak.leak(java.lang.String)')."
                    }
                },
                "required": ["file_path", "source", "sink"],
            },
        },
    }
    
}

all_function_list.append(taint_analysis_obj);

# def decompiler(file_path="", safe_location="", methods = None):
#     normalized_file_path = os.path.normpath(file_path)
#     normalized_safe_location = os.path.normpath(safe_location)

#     if file_path=="" or safe_location=="":
#         return json.dumps({"reply": "Error: No file path or location to safe the results was provided."});
#     if not os.path.exists(normalized_file_path):
#         return json.dumps({"reply": f"Error: File does not exist at path: {normalized_file_path}"})
#     if not os.path.exists(normalized_safe_location):
#         try:
#             os.makedirs(normalized_safe_location)
#         except OSError as e:
#             return json.dumps({"reply": f"Error: Safe location does not exist and can't be created: {normalized_safe_location}"})          
    
    
#     answer = decompile_write(normalized_file_path, normalized_safe_location, methods);
#     return json.dumps({"reply": answer})

# decompiler_obj = {
#     "function": decompiler,
#     "definition": {
#         "type": "function",
#         "function": {
#             "name": "decompiler",
#             "description": "Decompiles a java class file or jar file, by using a tool called cfr decompiler.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "file_path": {
#                         "type": "string",
#                         "description": "Path to a class file or jar file to be decompiled (e.g. '/usr/home/filename.class' or '/usr/home/filename.jar')."
#                     },
#                     "safe_location": {
#                         "type": "string",
#                         "description": "Path to the directory where the decompiled files should be stored (e.g. '/usr/home/'). If the user forgets the '/' at the end of directory name just add it."
#                     },
#                     "methods":{
#                         "type": "string",
#                         "description": "The user can also specify a method name to only decompile this method (e.g. 'main')."
#                     }
#                 },
#                 "required": ["file_path", "safe_location"],
#             }
#         }
#     }
# }


# all_function_list.append(decompiler_obj);

def decompiler_no_write(file_path="", methods = None):
    normalized_file_path = os.path.normpath(file_path)
    answer = ""

    log("Call of function 'decompiler_no_write' with the following file path (normalized): ", normalized_file_path, " methods ", methods)

    if file_path=="":
        log("The execution wasn't succesful and resulted in the following error: No file path was provided.")
        return json.dumps({"reply": "Error: No file path was provided."});
    if not os.path.exists(normalized_file_path):
        log("The execution wasn't succesful and resulted in the following error: File does not exist at path: ", normalized_file_path)
        return json.dumps({"reply": f"Error: File does not exist at path: {normalized_file_path}"})
    
    if not normalized_file_path.endswith(".jar") and not normalized_file_path.endswith(".class"):
        class_files = []
        log("No .jar or .class provided, searching for .class files in the directory: ", normalized_file_path)
        for root, dirs, files in os.walk(normalized_file_path):
            for file in files:
                if file.endswith(".class"):
                    class_files.append(os.path.join(root, file))

        if class_files == []:
            log("No class files found in the directory.")
            return json.dumps({"reply": "No class files found in the directory."})
        else:
            log("Class files found in the directory: ")
        for class_file in class_files:
            log(class_file)
            answer+= decompile_no_write(class_file, None)
    else:
        answer = decompile_no_write(normalized_file_path, methods);
    
    log("The execution was succesful and resulted in the following output: ", answer)
    return json.dumps({"reply": answer})

decompile_and_analyze_or_print_obj = {
    "function": decompiler_no_write,
    "definition": {
        "type": "function",
        "function": {
            "name": "decompile_and_analyze_or_print",
            "description": "Decompiles a java class file or jar file or all class files in a directory and returns the decompiled code. This function can be used, if the user asks you to analyze a code for yourself or if he just wants you to print out the decompiled code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to a class file or jar file to be decompiled (e.g. '/usr/home/filename.class' or '/usr/home/filename.jar'). It can also be a path to a directory containing class files (e.g. /usr/home/ bzw. /usr/home (in this cas just add the / at the end))."
                    },
                    "methods":{
                        "type": "string",
                        "description": "The user can also specify a method name to only decompile this method (e.g. 'main')."
                    }
                },
                "required": ["file_path"],
            }
        }
    }
}

all_function_list.append(decompile_and_analyze_or_print_obj)