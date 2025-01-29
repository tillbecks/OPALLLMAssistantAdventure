from groq import Groq
import json
from secret_keys import CROQ_SECRET_API_KEY, PATH_OPAL
from memory import Memory
from functions import all_function_list
import os

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
tools = map(lambda obj: obj["definition"], all_function_list)

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
            "- Suggesting an analysis using the heuristic function, and explaining to them how these would help them and why they were suggested\n" +
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
        available_functions = {
            obj["definition"]["function"]["name"]: obj["function"] for obj in all_function_list

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
    
