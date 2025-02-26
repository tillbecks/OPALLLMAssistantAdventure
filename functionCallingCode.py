from groq import Groq
import json
from secret_keys import CROQ_SECRET_API_KEY, PATH_OPAL
from memory import Memory
from functions import all_function_list
import os
from logger import initialize_logger, log

#Prompts examples:
#user_prompt1 = "Hello, how are you?"
#user_prompt2 = "Please do a constant string analysis on the file '/home/till/Schreibtisch/Uni/SoftwareDevelopmentTools/StringConstantsDemo.class'"
#user_prompt3 = "Please do a field assignability analysis on the file '/home/till/Schreibtisch/Uni/SoftwareDevelopmentTools/FieldAssignabilityDemo.class'"

#SBT_PATH = r"C:\Program Files (x86)\sbt\bin\sbt.bat"  # Comment this out


client = Groq(api_key=CROQ_SECRET_API_KEY)
Model = 'llama-3.3-70b-versatile'

#Initialisation of the memory component
mem = Memory()

if not os.path.exists(PATH_OPAL):
    raise Exception(f"OPAL directory not found at: {PATH_OPAL}")

if not os.path.exists(os.path.join(PATH_OPAL, "build.sbt")):
    raise Exception(f"No build.sbt found in OPAL directory: {PATH_OPAL}")

#In the following, all available functions are defined. Based on the Information in this list, the LLM makes a decision which function to call.


#Main function to run the conversation, receiving the user input and returning the LLMs response.
def run_conversation(user_prompt):
    log(f"User input: {user_prompt}")
    messages = [
        {
            "role": "system",
            "content": "You are a polite function calling LLM that uses the static analysis software Opal." + 
            "Opal combines different tools to analyse java bytecode. " +
            "Before, and only before, running any analysis:\n" +
            "If the user asks for suggestions, use the function meant for it. \n"+
            "You must only use the provided tools to answer. If a tool is required, invoke it exactly as defined.\n" +
            "Don't run two different analysis in one go\n"+
            "If the user is asking you something you can't answer, be honest and tell the user that you can't help with that. You NEVER lie or make stuff up." + 
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

    tools = map(lambda obj: obj["definition"], all_function_list)

    #The LLM is then called twice, ones to decide whether to call a tool and the second time to create a user-response based on the tools output (or if no tool call was decided based on the user input solely).
    response = client.chat.completions.create(
        model = Model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        max_tokens=4096,
        temperature= 0.2,
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    #If a tool call was decided, the chosen functions are being called and the output is being appended to the message.
    if tool_calls:
        log("The LLM decided to call a function.")
        available_functions = {
            obj["definition"]["function"]["name"]: obj["function"] for obj in all_function_list
        }
        messages.append(response_message)

        if len(tool_calls) > 1:
            log("The LLM decided to call more than one function. This is not allowed. We will only call the first function.")

        tool_call = tool_calls[0]
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
        log("The LLM decided to not call a function.")
        response = client.chat.completions.create(
            model=Model,
            messages=messages,
            max_tokens=4096
        )
        #messages.append(response_message) #I think this line is useless, as nothing is done with the message after this line and it is not stored permanently.
        final_response = response.choices[0].message.content

    mem.insert("user_input", user_prompt)
    mem.insert("llm_response", final_response)
    log(f"LLM response: {final_response}")
    return final_response

#The main loop running the conversation. The user can type in questions and a response is being generated by the LLM.
initialize_logger()
ui = "";
print("Hello, please type your question or 'q' to quit.\n")

while(ui != "q"):    
    print("You: ")
    ui = str(input())
    if(ui != "q"):
        print("\nAssistant: \n"+run_conversation(ui)+"\n")
    
