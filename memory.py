import datetime
import json

#A class to safe the conversation between the user and the LLM.
#The conversation is being stored in a list, which is being used as a stack.
#Every item in the memory contains a type of the message ment to hold info about who sent the message and the content of the message.
class Memory:
    #The constructor of the Memory class. It initializes the memory list and sets the maximum size of the memory.
    def __init__(self, max_size=30):
        self.memory = []
        self.max_size = max_size

    #A method to get the memory. It returns the in newest_count specified amount of memory entries or all if it isn't specified.
    def get(self, newest_count=-1):
        if newest_count > len(self.memory) or newest_count < 0:
            newest_count = len(self.memory)
        return self.memory[:newest_count]
    
    #Returns the memory in a textual format.
    def get_json_textual(self, newest_count=-1):
        content = ""
        if newest_count > len(self.memory) or newest_count < 0:
            newest_count = len(self.memory)
        for i in reversed(range(newest_count)):
            content += self.memory[i]["type"] + ": " + self.memory[i]["content"] + "\n"
        return content

    #A method to insert a new memory entry. It inserts the new entry at the beginning of the memory list and removes the last entry if the memory is too big.
    def insert(self, arg_type, content):
        self.memory.insert(0, {"type": arg_type, "content": content})
        if len(self.memory) > self.max_size:
            self.memory.pop()
