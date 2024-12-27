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
