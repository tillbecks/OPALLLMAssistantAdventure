from groq import Groq
import subprocess
import json
import os
from secret_keys import CROQ_SECRET_API_KEY
from memory import Memory

#Prompts examples:
#user_prompt1 = "Hello, how are you?"
#user_prompt2 = "Please do a constant string analysis on the file '/home/till/Schreibtisch/Uni/SoftwareDevelopmentTools/StringConstantsDemo.class'"
#user_prompt3 = "Please do a field assignability analysis on the file '/home/till/Schreibtisch/Uni/SoftwareDevelopmentTools/FieldAssignabilityDemo.class'"


client = Groq(api_key=CROQ_SECRET_API_KEY)
Model = 'llama3-70b-8192'

PATH_OPAL = "/home/till/Schreibtisch/Uni/SoftwareDevelopmentTools/opal" #Change this to your opal directory

mem = Memory()


def get_response(question):
    return json.dumps({"question": question})

def list_functions():
    response = ""
    for tool in tools:
        response += tool["function"]["name"] + ": " + tool["function"]["description"] + "\n"
    return json.dumps({"reply": "You are able to use the following functions: " + response})

def get_functions():
    return json.dumps({"reply": json.dumps(tools)})


def hierarchy_visualisation(file_path, safe_path=""):
    normalized_path = os.path.normpath(file_path)
    normalized_safe_path = os.path.normpath(safe_path)

    try:
        sbt_command = "project Tools; runMain org.opalj.support.debug.ClassHierarchyVisualizer " + normalized_path
        answer = run_sbt_command(sbt_command)
        return_message = ""
        #This function is disabled for now, because getting an file not found error, because the file the content is written first to is open in a file editor, when the sbt command is called, which somehow causes the error.
        if safe_path!="":
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
                return_message += "The following error occured while trying to safe the generated file in the specified safe_path: " + str(e) + " But it was safed in the file specified by the following output:"
        return_message += answer
        return json.dumps({"reply": return_message})
    except subprocess.CalledProcessError as e:
        return json.dumps({"reply": "The following error occured: " + str(e)})

def bytecode_disassembler(file_path, safe_path, disassembled_file_name=""):
    normalized_path = os.path.normpath(file_path)
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

def string_constants_analysis(file_path):
    normalized_path = os.path.normpath(file_path)
    
    sbt_command = "project Tools; runMain org.opalj.support.info.StringConstants -cp=" + normalized_path
    try:
        answer = run_sbt_command(sbt_command)
    except subprocess.CalledProcessError as e:
        return json.dumps({"reply": "The following error occured: " + str(e)})
    except FileNotFoundError:
        return json.dumps({"reply": "FileNotFoundError"})
    
    return json.dumps({"reply": answer})

def field_assignability_analysis(file_path):
    normalized_path = os.path.normpath(file_path)
    sbt_command = "project Demos; runMain org.opalj.fpcf.analyses.FieldAssignabilityAnalysisDemo -cp=" + normalized_path 
    try:
        answer = run_sbt_command(sbt_command)
    except subprocess.CalledProcessError as e:
        return json.dumps({"reply": "The following error occured: " + str(e)})
    except FileNotFoundError:
        return json.dumps({"reply": "FileNotFoundError"})
    
    return json.dumps({"reply": answer}) 

def field_array_usage_analysis(file_path):
    normalized_path = os.path.normpath(file_path)
    sbt_command = "project Demos; runMain org.opalj.tac.FieldAndArrayUsageAnalysis -cp=" + normalized_path
    try:
        answer = run_sbt_command(sbt_command)
    except subprocess.CalledProcessError as e:
        return json.dumps({"reply": "The following error occured: " + str(e)})
    except FileNotFoundError:
        return json.dumps({"reply": "FileNotFoundError"})
    return json.dumps({"reply": answer})

def local_points_to(file_path, method):
    normalized_path = os.path.normpath(file_path)
    sbt_command = "project Demos; runMain org.opalj.tac.LocalPointsTo "+ normalized_path + " " + method
    try:
        answer = run_sbt_command(sbt_command)
    except subprocess.CalledProcessError as e:
        return json.dumps({"reply": "The following error occured: " + str(e)})
    except FileNotFoundError:
        return json.dumps({"reply": "FileNotFoundError"})
    return json.dumps({"reply": answer})

def print_tac(file_path, method):
    normalized_path = os.path.normpath(file_path)
    sbt_command = "project Demos; runMain org.opalj.tac.PrintTAC "+ normalized_path + " " + method
    try:
        answer = run_sbt_command(sbt_command)
    except subprocess.CalledProcessError as e:
        return json.dumps({"reply": "The following error occured: " + str(e)})
    except FileNotFoundError:
        return json.dumps({"reply": "FileNotFoundError"})
    return json.dumps({"reply": answer})
    
def field_immutability_analysis(file_path):
    normalized_path = os.path.normpath(file_path)
    sbt_command = "project Demos; runMain org.opalj.fpcf.analyses.FieldImmutabilityAnalysisDemo -cp=" + normalized_path 
    try:
        answer = run_sbt_command(sbt_command)
    except subprocess.CalledProcessError as e:
        return json.dumps({"reply": "The following error occured: " + str(e)})
    except FileNotFoundError:
        return json.dumps({"reply": "FileNotFoundError"})
    
    return json.dumps({"reply": answer})  

def  run_sbt_command(command):
    return subprocess.run(["sbt", command], cwd=PATH_OPAL, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
    

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
                    #"safe_path": {
                    #    "type": "string",
                    #    "description": "optional path to the directory where the generated file should be stored (e.g. '/usr/home/')"
                    #},
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
    }
]

def run_conversation(user_prompt):
    messages = [
        {
            "role": "system",
            "content": "You are a function calling LLM that uses the static analysis software Opal." + 
            "Opal combines different tools to analyse java bytecode." +
            "If the user is asking you something you can't answer, be honest and tell the user that you can't help with that." + 
            "You will get the console output of the tools you call, which can contain a lot of irrelevant information."  +
            "You can ignore this information and just return the relevant information to the user." +
            "You have a memory from the last interactions with the user, please use this as a context. If you don't have a context, just ignore this information." +
            mem.get_json_textual()
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    response = client.chat.completions.create(
        model = Model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=4096,
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

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

        second_response = client.chat.completions.create(
                model=Model,
                messages=messages
        )
        final_response = second_response.choices[0].message.content
    else:
        response = client.chat.completions.create(
            model=Model,
            messages=messages,
            max_tokens=4096
        )
        messages.append(response_message)
        final_response = response.choices[0].message.content
    
    mem.insert("llm_response", final_response)
    return final_response

ui = "";
print("Hello, please type your question or 'q' to quit.\n")

while(ui != "q"):    
    print("You: ")
    ui = str(input())
    if(ui != "q"):
        mem.insert("user_input", ui)
        print("\n Assistant: "+run_conversation(ui)+"\n")
    
