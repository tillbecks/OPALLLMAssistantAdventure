from groq import Groq
import subprocess
import json
import os

#Prompts examples:
#user_prompt1 = "Hello, how are you?"
#user_prompt2 = "Please do a constant string analysis on the file '/home/till/Schreibtisch/Uni/SoftwareDevelopmentTools/StringConstantsDemo.class'"
#user_prompt3 = "Please do a field assignability analysis on the file '/home/till/Schreibtisch/Uni/SoftwareDevelopmentTools/FieldAssignabilityDemo.class'"


secret_value = #Insert your secret key from groq
client = Groq(api_key=secret_value)
Model = 'llama3-70b-8192'

PATH_OPAL = "/home/till/Schreibtisch/Uni/SoftwareDevelopmentTools/opal" #Change this to your opal directory

def get_response(question):
    return json.dumps({"question": question})

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
                        "description": "Responding a casual chat",
                    }
                },
                "required": ["question"],
            },
        },
    },
    {
        "type": "function",
        "function":{
            "name": "string_constants_analysis",
            "description": "conduct a string constants analysis on the java bytecode specified in the file path",
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
            "description": "conduct a field assignability analysis on the java bytecode specified in the file path",
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
]

def run_conversation(user_prompt):
    messages = [
        {
            "role": "system",
            "content": "You are a function calling LLM that uses the static analysis software Opal. Opal combines different tools to analyse java bytecode."
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
        max_tokens=4096
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        available_functions={
            "get_response": get_response,
            "string_constants_analysis": string_constants_analysis,
            "field_assignability_analysis": field_assignability_analysis
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
    
    return final_response

ui = "";
print("Hello, please type your question or 'q' to quit.\n")

while(ui != "q"):    
    ui = str(input())
    if(ui != "q"):
        print("\n"+run_conversation(ui)+"\n")
    
