from code import interact
import json
from random import choice
import pathlib

class rule:

    def __init__(self, id:str, conditions: list, actions: list) -> None:
        self.id = id
        self.conditions = conditions
        self.actions = actions
        self.activated = False
        if any([action["func"]=="yes_or_no" or action["func"]=="ask_int" for action in self.actions]):
            self.requires_input = True
        else:
            self.requires_input = False

class machine:

    def __init__(self, jsonfile: str) -> None:

        self.raw_data = {}
        self.rules = {}
        self.answered = {}

        with open(jsonfile, "r", encoding='utf-8') as read_rules:
            self.raw_data = json.load(read_rules)

        for id, info in self.raw_data.items():
            self.rules[id] = rule(id, info["conditions"], info["actions"])

        for r in self.rules.values():
            for condition in r.conditions:
                if isinstance(condition, list):
                    self.answered[condition[0]] = None
    
    def perform_actions(self, rule_id: str) -> None:
        for action in self.rules[rule_id].actions:
            if action["func"] == "ask_int":
                self.answered[action["arg_1"]] = self.ask_int(action["arg_2"])
            elif action["func"] == "yes_or_no":
                self.answered[action["arg_1"]] = self.yes_or_no(action["arg_2"])
            elif action["func"] == "assert":
                self.answered[action["arg_1"]] = action["arg_2"]
            elif action["func"] == "print":
                self.print(action["arg_1"])
    
    @staticmethod
    def ask_int(question: str) -> int:
        while True:
            answer = input(question)
            try:
                answer = int(answer)
                return answer
            except:
                continue

    @staticmethod
    def yes_or_no(question: str) -> str:
        while True:
            answer = input(question)
            if answer.lower() in ["yes", "y"]:
                return "yes"
            elif answer.lower() in ["no", "n"]:
                return "no"
    
    @staticmethod
    def print(text: str) -> None:
        print(text)
    
    def interprete(self, rule_id: str) -> tuple:
        text = ""
        for item in self.rules[rule_id].conditions:
            temp = ""
            if isinstance(item, list):
                temp += f"self.answered[\"{item[0]}\"]"
                if item[1] == "eq":
                    temp += " == "
                elif item[1] == ">":
                    temp += " > "
                elif item[1] == "<":
                    temp += " < "
                if item[2] == "null":
                    temp += "None"
                elif isinstance(item[2], int):
                    temp += f"{item[2]}"
                else:
                    temp += f"\"{item[2]}\""
            elif isinstance(item, str):
                temp = f" {item} "
            text += temp
        
        try:
            ready = eval(text)
        except:
            ready = False
        
        return text, ready
    
    def run(self) -> None:
        while True:
            # asking for input
            options = []
            for rule in self.rules.values():
                cond, ready = self.interprete(rule.id)
                if ready == True and rule.activated == False:
                    options += [rule.id]
            try:
                chosen_rule = choice(options)
                self.perform_actions(chosen_rule)
                self.rules[chosen_rule].activated = True
            except:
                break
            self.implications()

    def implications(self):
        # calculating implications
        while True:
            done = True
            for rule in self.rules.values():
                cond, ready = self.interprete(rule.id)
                if  ready == True and rule.activated == False and rule.requires_input == False:
                    self.perform_actions(rule.id)
                    rule.activated = True
                    done = False
                    break
            if done == True:
                break
        
def main():

    DEBUG = False

    jsonfile = pathlib.Path(__file__).parent.resolve()
    jsonfile = str(jsonfile) + "/rules.json"
    m = machine(jsonfile)

    if DEBUG == False:
        m.run()
    elif DEBUG == True:
        #m.perform_actions("ask-if-read-sharp-objects")
        m.perform_actions("ask-temp")
        m.implications()

if __name__ == "__main__":
    main()
