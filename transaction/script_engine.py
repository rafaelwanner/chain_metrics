


class ScriptEngine():
    def __init__(self):
        self.type = 0
        self.locking = 0
        self.unlocking = 0
        
        self.loaded = False
        
    def load(self, script):
        self.type = script['locking_script_type']
        self.locking = script['locking_script_data']
        self.unlocking = script['unlocking_script']

        self.loaded = True

    def execute(self):
        if not self.loaded:
            print("Cannot execute! Load first.")

