#Exstracted from source notebook with relative path this files initial creation: ../pytest_test_dir/Dummy_CPU_DevNB.ipynb


import pytest


from .. import simple_cpu



alu = ALU()

def test_add():
    assert alu.add(5, 3) == 8, "Addition test failed"

def test_subtract():
    assert alu.subtract(10, 4) == 6, "Subtraction test failed"

def test_bitwise_and():
    assert alu.bitwise_and(5, 3) == 1, "Bitwise AND test failed"



def test_load_store():
    cu = ControlUnit(ALU())
    cu.load("address1", 10)
    assert cu.store("address1") == 10, "LOAD/STORE test failed"

def test_execute_add():
    cu = ControlUnit(ALU())
    assert cu.execute("ADD", 5, 3) == 8, "Execute ADD test failed"

def test_execute_subtract():
    cu = ControlUnit(ALU())
    assert cu.execute("SUBTRACT", 10, 4) == 6, "Execute SUBTRACT test failed"

def test_execute_and():
    cu = ControlUnit(ALU())
    assert cu.execute("AND", 5, 3) == 1, "Execute AND test failed"



def test_ram_write_and_read():
    ram = RAM()
    ram.write("address1", "data1")
    assert ram.read("address1") == "data1", "Failed to read the written data correctly"

def test_ram_read_empty_address():
    ram = RAM()
    assert ram.read("address2") is None, "Reading from an empty address should return None"



def test_rom_read_preloaded_data():
    preloaded_data = {"address1": "data1", "address2": "data2"}
    rom = ROM(preloaded_data)
    assert rom.read("address1") == "data1", "Failed to read preloaded data correctly"

def test_rom_read_nonexistent_address():
    preloaded_data = {"address1": "data1"}
    rom = ROM(preloaded_data)
    assert rom.read("address3") is None, "Reading from a nonexistent address should return None"
