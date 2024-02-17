#Exstracted from source notebook with relative path this files initial creation: ../Dummy_CPU_DevNB.ipynb


########
### Arithmetic logic unit (ALU)
#dummy ALU that only has three functions:
#* *add* two inputs
#* *subtract* two inputs
#* *bitwise_and* two inputs
########



class ALU:
    def __init__(self):
        pass

    def add(self, a, b):
        print(f"ALU:add: {a=}, {b=}; {a + b =}")
        return a + b

    def subtract(self, a, b):
        print(f"ALU:subtract: {a=}, {b=}; {a - b =}")
        return a - b

    def bitwise_and(self, a, b):
        print(f"ALU:bitwise_and: {a=}, {b=}; {a & b =}")
        return a & b


########
## Control Unit (CU)
#Dummy control unit that works with our dummy ALU above that has the following functions:
#* *load* a value to a given address
#* *store* return a value at a given address
#* *execute* performs a ALU function based on the input command with two inputs; if the given command is not in the above ALU will return `"Unknown command"`
########



class ControlUnit:
    def __init__(self, alu):
        self.alu = alu
        self.memory = {}  # Simulating memory with a dictionary

    def load(self, address, value):
        """Load a value into a specified memory address."""
        print(f"CU:load: {address=}, {value=}")
        self.memory[address] = value

    def store(self, address):
        """Store and return the value from a specified memory address."""
        print(f"CU:store: {address=}")
        return self.memory.get(address, None)

    def execute(self, command, a, b):
        """Execute an ALU operation."""
        print(f"CU:execute: {command=}, {a=}, {b=} ")

        match command:
            case 'ADD':
                return self.alu.add(a, b)
            case 'SUBTRACT':
                return self.alu.subtract(a, b)
            case 'AND':
                return self.alu.bitwise_and(a, b)
            case _:
                print('CU:execute: received an  Unknown command')
                return "Unknown command"


########
## Random Access Memory (RAM)
#Dummy RAM that has the following functions:
#* *write* will write a value to a given address
#* *read* will retrieve a value at a given address
########



class RAM:
    def __init__(self):
        self.storage = {}

    def write(self, address, data):
        """Write data to a specific address in RAM."""
        print(f"RAM:write: {address=}, {data=}")
        self.storage[address] = data

    def read(self, address):
        """Read data from a specific address in RAM. Returns None if the address is empty."""
        print(f"RAM:read: {address=}")
        return self.storage.get(address, None)


########
## Read-Only Memory (ROM)
#Dummy ROM that has the following functions:
#* *read* will retrieve a value at a given address
########



class ROM:
    def __init__(self, preloaded_data):
        """
        Initialize the ROM with preloaded data.
        preloaded_data should be a dictionary mapping addresses to their contents.
        """
        self.storage = preloaded_data

    def read(self, address):
        """Read data from a specific address in ROM. Returns None if the address does not exist."""
        print(f"ROM:read: {address=}")
        return self.storage.get(address, None)
