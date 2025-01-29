from groq import Groq
import subprocess
import json
import os
from secret_keys import CROQ_SECRET_API_KEY
from memory import Memory
import os.path

#Prompts examples:
#user_prompt1 = "Hello, how are you?"
#user_prompt2 = "Please do a constant string analysis on the file '/home/till/Schreibtisch/Uni/SoftwareDevelopmentTools/StringConstantsDemo.class'"
#user_prompt3 = "Please do a field assignability analysis on the file '/home/till/Schreibtisch/Uni/SoftwareDevelopmentTools/FieldAssignabilityDemo.class'"

#SBT_PATH = r"C:\Program Files (x86)\sbt\bin\sbt.bat"  # Comment this out

client = Groq(api_key=CROQ_SECRET_API_KEY)
Model = 'llama-3.3-70b-versatile'

PATH_OPAL = "C:\\Users\\anach\\Documents\\Masters\\SDT\\opal" #Change this to your opal directory

#Initialisation of the memory component
mem = Memory()

if not os.path.exists(PATH_OPAL):
    raise Exception(f"OPAL directory not found at: {PATH_OPAL}")

if not os.path.exists(os.path.join(PATH_OPAL, "build.sbt")):
    raise Exception(f"No build.sbt found in OPAL directory: {PATH_OPAL}")

#A Function to respond to a casual chat
def get_response(question):
    return json.dumps({"question": question})

#A Function that lists all available functions
def list_functions():
    response = ""
    for tool in tools:
        response += tool["function"]["name"] + ": " + tool["function"]["description"] + "\n"
    return json.dumps({"reply": "You are able to use the following functions: " + response})

#This creates a gv file of the class hierarchy of a jar file. Currently a safe_path to save the visualisation at can't be created.
def hierarchy_visualisation(file_path, safe_path=""):
    normalized_path = os.path.normpath(file_path)

    if not os.path.exists(normalized_path):
        return json.dumps({"reply": f"Error: File does not exist at path: {normalized_path}"})

    normalized_safe_path = os.path.normpath(safe_path)

    try:
        sbt_command = "project Tools; runMain org.opalj.support.debug.ClassHierarchyVisualizer " + normalized_path
        answer = run_sbt_command(sbt_command)
        return_message = ""
        #This functionality is disabled for now, because getting an file not found error, because the file the content is written first to is open in a file editor, when the sbt command is called, which somehow causes the error.
        '''if safe_path!="":
            try:
                find_answer = answer.find("Wrote class hierarchy graph to:")
                if find_answer != -1:
                    jar_name = normalized_path.split("/")[-1].split(".")[0] + ".gv"
                    normalized_safe_path = os.path.join(normalized_safe_path, jar_name)
                    #Am ende hinter dem Pfad der nachricht ist noch ein Punkt, der ignoriert werden muss
                    print(answer)
                    safe_path_new = os.path.normpath(answer[find_answer+30:].split("\n")[0][:-1])
                    print(safe_path_new)
                    content = open(safe_path_new, "r").read().close();
                    print(normalized_safe_path)
                    open(normalized_safe_path, "w").write(content).close();
                    return json.dumps({"reply": "The class hierarchy has been stored in the file " + normalized_safe_path + ". A copy of the file has been safed at: " + safe_path_new})
            except Exception as e:
                print(e)
                return_message += "The following error occured while trying to safe the generated file in the specified safe_path: " + str(e) + " But it was safed in the file specified by the following output:"'''
        return_message += answer
        return json.dumps({"reply": return_message})
    except subprocess.CalledProcessError as e:
        return json.dumps({"reply": "The following error occured: " + str(e)})

#This function creates a html file, that visualizes the disassembled bytecode of a class file. The file is stored in the safe_path if specified, otherwise in the same directory as the class file.
def bytecode_disassembler(file_path, safe_path, disassembled_file_name=""):
    normalized_path = os.path.normpath(file_path)

    if not os.path.exists(normalized_path):
        return json.dumps({"reply": f"Error: File does not exist at path: {normalized_path}"})

    normalized_safe_path = os.path.normpath(safe_path)

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

        #return json.dumps({"reply": "The disassembled file has been stored in the path " + os.path.join(safe_path, safe_file + ".html") + "."})
        return json.dumps({"reply": answer})

    except subprocess.CalledProcessError as e:
        return json.dumps({"reply": "The following error occured: " + str(e)})
    except FileNotFoundError: 
        return json.dumps({"reply": "FileNotFoundError"})
    except PermissionError:
        return json.dumps({"reply": "PermissionError while trying to write the disassembled file to the specified path."})

#This function conducts a string constants analysis on the java bytecode specified in the file path.
def string_constants_analysis(file_path):
    
    normalized_path = os.path.normpath(file_path)
    
    if not os.path.exists(normalized_path):
        return json.dumps({"reply": f"Error: File does not exist at path: {normalized_path}"})
    
    sbt_command = f'project Tools; runMain org.opalj.support.info.StringConstants -cp={normalized_path}'
    
    try:
        answer = run_sbt_command(sbt_command)
    except subprocess.CalledProcessError as e:
        return json.dumps({"reply": f"The following error occurred: {str(e)}"})
    except FileNotFoundError as e:
        return json.dumps({"reply": f"FileNotFoundError: Could not find file at path: {normalized_path}"})
    
    return json.dumps({"reply": answer})

#This function conducts a field assignability analysis on the java bytecode specified in the file path.
def field_assignability_analysis(file_path):
    normalized_path = os.path.normpath(file_path)

    if not os.path.exists(normalized_path):
        return json.dumps({"reply": f"Error: File does not exist at path: {normalized_path}"})

    sbt_command = "project Demos; runMain org.opalj.fpcf.analyses.FieldAssignabilityAnalysisDemo -cp=" + normalized_path

    try:
        answer = run_sbt_command(sbt_command)
    except subprocess.CalledProcessError as e:
        return json.dumps({"reply": "The following error occured: " + str(e)})
    except FileNotFoundError:
        return json.dumps({"reply": "FileNotFoundError"})
    
    return json.dumps({"reply": answer}) 

#This function conducts a field array usage analysis on the java bytecode specified in the file path.
def field_array_usage_analysis(file_path):
    normalized_path = os.path.normpath(file_path)

    if not os.path.exists(normalized_path):
        return json.dumps({"reply": f"Error: File does not exist at path: {normalized_path}"})

    sbt_command = "project Demos; runMain org.opalj.tac.FieldAndArrayUsageAnalysis -cp=" + normalized_path
    try:
        answer = run_sbt_command(sbt_command)
    except subprocess.CalledProcessError as e:
        return json.dumps({"reply": "The following error occured: " + str(e)})
    except FileNotFoundError:
        return json.dumps({"reply": "FileNotFoundError"})
    return json.dumps({"reply": answer})

#This function collects points-to information related to a method in a specific class or jar file.
def local_points_to(file_path, method="main"):

    normalized_path = os.path.normpath(file_path)
    
    if not os.path.exists(normalized_path):
        return json.dumps({"reply": f"Error: File does not exist at path: {normalized_path}"})
    
    # Format the command with proper quoting
    sbt_command = f'project Demos; runMain org.opalj.tac.LocalPointsTo -cp={normalized_path} {method}'
    
    try:
        answer = run_sbt_command(sbt_command)
    except subprocess.CalledProcessError as e:
        return json.dumps({"reply": "The following error occured: " + str(e)})
    except FileNotFoundError:
        return json.dumps({"reply": "FileNotFoundError"})
    return json.dumps({"reply": answer})

#This function prints the complete three address code representation of a method in a specific class or jar file.
#But the LLM tends to only show the three address code related to the specified function, even though the the opal function returns the tac of the whole class.
def print_tac(file_path, method="main"):
    normalized_path = os.path.normpath(file_path)

    if not os.path.exists(normalized_path):
        return json.dumps({"reply": f"Error: File does not exist at path: {normalized_path}"})

    sbt_command = "project Demos; runMain org.opalj.tac.PrintTAC "+ normalized_path + " " + method

    try:
        answer = run_sbt_command(sbt_command)
    except subprocess.CalledProcessError as e:
        return json.dumps({"reply": "The following error occured: " + str(e)})
    except FileNotFoundError:
        return json.dumps({"reply": "FileNotFoundError"})
    return json.dumps({"reply": answer})
    
#This function conducts a field immutability analysis on the java bytecode specified in the file path.
def field_immutability_analysis(file_path):
    normalized_path = os.path.normpath(file_path)

    if not os.path.exists(normalized_path):
        return json.dumps({"reply": f"Error: File does not exist at path: {normalized_path}"})

    sbt_command = "project Demos; runMain org.opalj.fpcf.analyses.FieldImmutabilityAnalysisDemo -cp=" + normalized_path 

    try:
        answer = run_sbt_command(sbt_command)
    except subprocess.CalledProcessError as e:
        return json.dumps({"reply": "The following error occured: " + str(e)})
    except FileNotFoundError:
        return json.dumps({"reply": "FileNotFoundError"})
    
    return json.dumps({"reply": answer})

#This function conducts a parameter usage analysis on the java bytecode specified in the file path.
def parameter_usage_analysis(file_path):
    normalized_path = os.path.normpath(file_path)

    if not os.path.exists(normalized_path):
        return json.dumps({"reply": f"Error: File does not exist at path: {normalized_path}"})

    sbt_command = "project Demos; runMain org.opalj.ai.domain.l0.ParameterUsageAnalysis -cp=" + normalized_path 
    try:
        answer = run_sbt_command(sbt_command)
    except subprocess.CalledProcessError as e:
        return json.dumps({"reply": "The following error occured: " + str(e)})
    except FileNotFoundError:
        return json.dumps({"reply": "FileNotFoundError"})
    
    return json.dumps({"reply": answer})


#Just a helper funtion to run sbt commands in the opal directory specified by the user. 
def run_sbt_command(command):
    
    # Format the command as a single string
    full_command = f'sbt "{command}"'
    
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
        return result.stdout
    except FileNotFoundError as e:
        print(f"SBT not found in PATH. Error: {e}")
        print(f"Current PATH: {os.environ.get('PATH', '')}")
        raise e
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
        print(f"Error output: {e.stderr}")
        raise e

#In the following, all available functions are defined. Based on the Information in this list, the LLM makes a decision which function to call.
tools = [
    {
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
    },
    {
        "type": "function",
        "function": {
            "name": "list_functions",
            "description": "Returns the json containing all of your callable functions, what they do and what parameters they use. Use this function to retrieve information about available capabilities or needed parameters instead of directly calling other functions." + 
            "e.g. 'Please list all functions' or 'What parameters does the function  xy need?'",
        },
    },
    {
        "type": "function",
        "function":{
            "name": "string_constants_analysis",
            "description": "Uses Opal to conduct a string constants analysis on the java bytecode specified in a file path.",
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
    },
    {
        "type": "function",
        "function":{
            "name": "field_assignability_analysis",
            "description": "Conducts a field assignability analysis on the java bytecode specified in the file path.",
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
    },
    {
        "type": "function",
        "function":{
            "name": "field_immutability_analysis",
            "description": "conduct a field immutability analysis on the java bytecode specified in the file path",
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
    },
    {
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
    },
    {
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
        }
    },
    {
        "type": "function",
        "function": {
            "name": "field_array_usage_analysis",
            "description": "Conducts a field array usage analysis on the java bytecode specified in the class or jar file specified in the path.",
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
    },
    {
        "type": "function",
        "function": {
            "name": "local_points_to",
            "description": "Collect points-to information related to a method in a specific class or jar file.",
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
                }
            }
        }
    },
    {
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
                }
            }
        },
    },
    {
        "type": "function",
        "function":{
            "name": "parameter_usage_analysis",
            "description": "conduct a parameter usage analysis on the java bytecode specified in the file path",
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
    },
    {
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
]


def suggest_analysis(file_path):
    """Suggests a specific OPAL analysis based on bytecode patterns."""
    normalized_path = os.path.normpath(file_path)

    if not os.path.exists(normalized_path):
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

        return json.dumps({"reply": "Recommended analyses:\n" + "\n".join(suggestions)})

    except subprocess.CalledProcessError:
        return json.dumps({"reply": "Error: Could not inspect bytecode."})

#Main function to run the conversation, receiving the user input and returning the LLMs response.
def run_conversation(user_prompt):
    messages = [
        {
            "role": "system",
            "content": "You are a function calling LLM that uses the static analysis software Opal. " + 
            "Opal combines different tools to analyse java bytecode. " +
            "Your capabilities include:\n" +
            "1. String Constants Analysis: Identifies and analyzes string constants in the bytecode\n" +
            "2. Field Assignability Analysis: Analyzes how fields can be assigned values\n" +
            "3. Field Array Usage Analysis: Examines how arrays are used within fields\n" +
            "4. Field Immutability Analysis: Determines if fields are effectively immutable\n" +
            "5. Parameter Usage Analysis: Analyzes how parameters are used in methods\n" +
            "6. Local Points-To Analysis: Tracks object references and their relationships\n" +
            "7. Bytecode Disassembler: Converts bytecode to human-readable format\n" +
            "8. Hierarchy Visualization: Visualizes class hierarchies from JAR files\n\n" +
            "Before, and only before, running any analysis:\n" +
            "1. If no .class file was given, ask for it"
            "2. Warn the user that the analysis may take several minutes to complete\n\n" +
            "To help you help the user, in case they don't know what analyses to run, you can also interact with them by:\n" +
            "- Suggesting an analysis using the heuristic function, and explaining to them how these would help them\n" +
            "- Asking about their specific needs or what they want to understand about their code\n" +
            "If the user is asking you something you can't answer, be honest and tell the user that you can't help with that. " + 
            "You will get the console output of the tools you call, which can contain a lot of irrelevant information. " +
            "You can ignore this information and just return the relevant information to the user. " +
            "You have a memory from the last interactions with the user, please use this as a context. If there is no memory following this, just ignore this information. " +
            mem.get_json_textual()
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    #The LLM is then called twice, ones to decide whether to call a tool and the second time to create a user-response based on the tools output (or if no tool call was decided based on the user input solely).
    response = client.chat.completions.create(
        model = Model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=4096,
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    #If a tool call was decided, the chosen functions are being called and the output is being appended to the message.
    if tool_calls:
        available_functions={
            "get_response": get_response,
            "list_functions": list_functions,
            "string_constants_analysis": string_constants_analysis,
            "field_assignability_analysis": field_assignability_analysis,
            "bytecode_disassembler": bytecode_disassembler,
            "hierarchy_visualisation": hierarchy_visualisation,
            "field_array_usage_analysis": field_array_usage_analysis,
            "local_points_to": local_points_to,
            "print_tac": print_tac,
            "field_immutability_analysis": field_immutability_analysis,
            "parameter_usage_analysis":parameter_usage_analysis,
            "suggest_analysis": suggest_analysis,
        }
        messages.append(response_message)


        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)
            

            messages.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response
            })

        #The second and final response is being created, which is going to be displayed to the user as the LLMs answer.
        second_response = client.chat.completions.create(
                model=Model,
                messages=messages
        )
        final_response = second_response.choices[0].message.content
    #If no tool call was decided, the LLMs response is being created based on the user input solely.
    else:
        response = client.chat.completions.create(
            model=Model,
            messages=messages,
            max_tokens=4096
        )
        #messages.append(response_message) #I think this line is useless, as nothing is done with the message after this line and it is not stored permanently.
        final_response = response.choices[0].message.content

    mem.insert("user_input", user_prompt)
    mem.insert("llm_response", final_response)
    return final_response

#The main loop running the conversation. The user can type in questions and a response is being generated by the LLM.
ui = "";
print("Hello, please type your question or 'q' to quit.\n")

while(ui != "q"):    
    print("You: ")
    ui = str(input())
    if(ui != "q"):
        print("\n Assistant: \n"+run_conversation(ui)+"\n")
    
