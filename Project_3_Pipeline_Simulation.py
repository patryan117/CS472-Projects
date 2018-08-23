# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 09:39:29 2017


Author: Patrick Ryan
Class:  Computer Architecture (Met CS 472)
Language Python 2.7


Simulation of a pipelining using pipeline datapath

- Pipeline is initialized to contain all NOP's before starting  (aka 0th iteration)
- The main program will have initialization codde, and then one big loop, where each time through the loop is euilaven to one cycle in a pipeline.
- The loop will call those five functions, print out the appropriate information, and then copy the write version of the pipeline registers into the read version for use in the next cycle.
- Control must use control bits, hosever they are not limited to a single bit ( so you can use a whole int to store each control signal)
- You will need a read and write version of the pipeline registers so that you wont overwrite a pipeline register by one stage before the other stage has had a chance to read it.
- Only instruction types used are add, subtract (sub), load byte (lb) and store byte (sb).
- This way you will only have to get a single btteout of the MM array.  (The same holds true true for sb)
- After each cycle, print out the Regs value  and both the read / write versions of all four pipeline registers.  (Do this before you copy at the very end of the cycle.)



""" 




import copy
import numpy as np
import pandas as pd


starting_address = 0x7A000
main_mem = []
main_mem_size = 2048 # (0x800)
main_mem_skip = 255  # (0xff - 1)
regs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,]

instructions = [0xA1020000, 0x810AFFFC, 0x00831820, 0x01263820, 0x01224820, 0x81180000, 0x81510010, 0x00624022, 0x00000000, 0x00000000, 0x00000000, 0x00000000]  

"""
--------------------------------------------------------------------------------------------------------------------------------------------------------------
Signal Definitions:
--------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    RegDst: 
        If = 0; The register destination number for the Write register comes from the rt field (bits 20:16)
        if = 1; The register destination number for the Write register comes from the rd field (bits 15:11)
            
    RegWrite: 
        If = 0; none.
        If = 1; The register on the Write register input is written with the value on the Write data input.
        
    ALUSrc:
        If = 0; The second ALU operand comes from the second register file optput (read data 2)
        If = 1; The second ALU operand is the sign extended, lower 16 bits of the instruction
        
    MemRead:
        If = 0; None.
        If = 1; Data memory contents designated by the address input are put on the Read data output.
        
    MemWrite:
        If = 0; None.
        If = 1; Data memory contents designated by the address input are replaced by the value on the Write data input.
    
    MemtoReg:
        If = 0; The value fed to the register Write data input comes from the ALU.
        If = 1; The value fed to the register Write data input comes from the data memory.

--------------------------------------------------------------------------------------------------------------------------------------------------------------

R-type instructions

    IF: Instruction fetch
        • IR <-- IMemory[PC] 
        • PC <-- PC + 4
    ID: Instruction decode/register fetch
        • A <-- Register[IR[25:21]] 
        • B <-- Register[IR[20:16]]
    Ex: Execute
        • ALUOutput <-- A op B
    MEM: Memory
        • nop
    WB: Write back
        • Register[IR[15:11]] <-- ALUOutput


        
Load instruction

    IF: Instruction fetch
        • IR <-- IMemory[PC] 
        • PC <-- PC + 4
    ID: Instruction decode/register fetch
        • A <-- Register[IR[25:21]] 
        • B <-- Register[IR[20:16]]
    Ex: Execute
        • ALUOutput <-- A + SignExtend(IR[15:0])
    MEM: Memory
        • Mem-Data <-- DMemory[ALUOutput]
    WB: Write back
        • Register[IR[20:16]] <-- Mem-Data
        
        
Store instruction

    IF: Instruction fetch
        • IR <-- IMemory[PC] 
        • PC <-- PC + 4
    ID: Instruction decode/register fetch
        • A <-- Register[IR[25:21]] 
        • B <-- Register[IR[20:16]]
    Ex: Execute
        • ALUOutput <-- A + SignExtend(IR[15:0])
    MEM: Memory
        • DMemory[ALUOutput] <-- B
    WB: Write back
        • nop  
        

        
-------------------------------------------------------------------------------------------------
        
        
opcode	   ALUOp	 operation	  funct field	        ALU action	        ALU cntl
LW	   00	       load word	  xxxxxx	        add	               010
SW	   00	       store word	  xxxxxx	        add	               010
BEQ	   01	       branch equal	  xxxxxx	        subtract	        110
R-type	   10	       add	         100000	        add	               010
R-type	   10	       subtract	  100010	        subtract	        110
R-type	   10	       AND	         100100	        and	               000
R-type	   10	       OR	         100101	        or	               001
R-type	   10	       SLT	         101010	        set on less than	  111        
        
"""
 


class If_id_class:

    def __init__(self, instruction, incr_pc): # Constructor to initiate IF/ID values to zero.
        self.instruction = instruction
        self.incr_pc = incr_pc        # Note: no clear function required for the IF/ID class.  
        
class Id_ex_class:  

    def __init__(self):    # Constructor to initiate ED/EX values to zero.
        self.instruction = 0
        self.instruction_type = ""
        self.alu_src = 0
        self.alu_op = 0
        self.function = 0
        self.incr_pc = 0
        self.mem_read = 0
        self.mem_to_reg = 0
        self.mem_write = 0
        self.opcode = 0      
        self.read_reg1_value = 0
        self.read_reg2_value = 0
        self.reg_dst = 0
        self.reg_write = 0
        self.sign_offset = 0
        self.write_reg_12_16 = 0
        self.write_reg_17_21 = 0

    def decode(self, instruction, incr_pc):  # Mips decoder (concepts from first project)
        self.instruction = instruction
        self.incr_pc = incr_pc
        opcode = bits1_6(instruction)
        self.opcode = opcode

        if opcode == 0: # R-type Instruction
            dest = bits17_21(instruction)
            src1 = bits7_11(instruction)        # SRC1 <-- Register[IR[25:21]] 
            src2 = bits12_16(instruction)       # SRC2 <-- Register[IR[20:16]]
            function = bits27_32(instruction)

            if function == 0b100000: # (Add Instruction)
                self.alu_op = 2    # Since R type
                self.alu_src = 0   
                self.function = 0b100000  
                self.mem_to_reg = 0 # Since R Type
                self.mem_read = 0  # Since not reading
                self.mem_write = 0  # Since not writing
                self.reg_dst = 1 # Coming from bits 15: 11
                self.reg_write = 1  # = 1 for all cases
                self.read_reg1_value = regs[src1] # SRC1 fed into the first register
                self.read_reg2_value = regs[src2] # SRC2 fed into the second register
                self.sign_offset = "X"    
                self.write_reg_12_16 = str(src2) # SRC2 value as bits 20:16
                self.write_reg_17_21 = str(dest) # Dest value as bits 25:21
                
            if function == 0b100010:  # (Subtract Instruction)
                self.alu_op = 2  # Since R Type
                self.alu_src = 0  # Since Load instruction
                self.reg_dst = 1 # Coming from bits 15: 11
                self.mem_to_reg = 0   # Since R type (value fed to the register write data input comes from the ALU)
                self.reg_write = 1 # = 1 for all cases 
                self.mem_read = 0  # Since not reading 
                self.mem_write = 0 # Since not writing
                self.function = 0b100010
                self.read_reg1_value = regs[src1] # SRC1 fed into the first register
                self.read_reg2_value = regs[src2] # SRC2 fed into the second register
                self.sign_offset = "X" # Junk
                self.write_reg_12_16 = str(src2)  # SRC2 value as bits 20:16
                self.write_reg_17_21 = str(dest)  # Dest value as bits 25:21
                
        else: # I FORMAT
            if opcode == 0b100000: # If load byte
                src1 = bits7_11(instruction) # SRC1 <-- Register[IR[25:21]]
                dest = bits12_16(instruction) # SRC2 <-- Register[IR[20:16]]
                offset = bits16_32(instruction)
                self.alu_op = 0  # Since I Type  (ALU option = Add)
                self.alu_src = 1  # Since I Type
                self.reg_dst = 0  # Not comming from bits 15:11 (20:16 instead to write register)
                self.mem_to_reg = 1  # Since load Instruction
                self.reg_write = 1  # = 1 for all cases
                self.mem_read = 1  # Since loading
                self.mem_write = 0  # since not writing to memory
                self.write_reg_12_16 = str(dest) # Write_Reg_20_16 == dest 
                self.write_reg_17_21 = 0  # Instructions 15:21 unused in load)
                self.read_reg1_value = regs[src1]  # Passed to read register 1
                self.read_reg2_value = regs[dest]  # Passed to read register 2
                self.function = 'X'   # Junk
                self.sign_offset = twos_comp(offset, 16)  # Extend offset

            elif opcode == 0b101000: # (If store byte)
                src1 = bits7_11(instruction)  # SRC1 <-- Register[IR[25:21]]
                dest = bits12_16(instruction) # SRC2 <-- Register[IR[20:16]]
                offset = bits16_32(instruction)
                self.alu_src = 1  # Since I type
                self.alu_op = 0  # Since I type  (ALU action = add)
                self.reg_dst = 'X' # Junk
                self.mem_to_reg = 'X' # Junk
                self.mem_read = 0  # Since not reading 
                self.mem_write = 1  # Since writing
                self.function = 'X'  # Junk
                self.write_reg_12_16 = str(dest) # Write_Reg_20_16 == dest 
                self.write_reg_17_21 = 0 # Instructions 15:21 unused in load)
                self.reg_write = 0  # = 1 for all cases
                self.read_reg1_value = regs[src1]  # Passed to read register 1
                self.read_reg2_value = regs[dest] # Passed to read register 2
                self.sign_offset = twos_comp(offset, 16) # Extend offset
                
    def clear(self):  # Clears all values in the ID/EX register
        self.instruction_type = ""
        self.reg_dst = 0
        self.alu_src = 0
        self.alu_op = 0
        self.mem_read = 0
        self.mem_write = 0
        self.mem_to_reg = 0
        self.reg_write = 0
        self.sign_offset = 0
        self.incr_pc = 0
        self.read_reg1_value = 0
        self.read_reg2_value = 0
        self.write_reg_17_21 = 0
        self.write_reg_12_16 = 0
        self.WriteReg1 = 0
        self.WriteReg2 = 0
        self.function = 0
        
class Ex_mem_class:  
    def __init__(self):  # Constructor to initiate EX/MEM values to zero
        self.instruction_type = ""
        self.mem_read = 0
        self.mem_write = 0
        self.mem_to_reg = 0
        self.reg_write = 0
        self.read_reg1_value = 0
        self.read_reg2_value = 0
        self.sign_offset = 0
        self.alu_op = 0
        self.incr_pc = 0
        self.alu_result = 0
        self.sb_value = 0
        self.write_reg = 0

    def execute(self, mem_read, mem_write, reg_write, alu_op, read_reg1_value, read_reg2_value, sign_offset, function, incrPC, opcode, reg_dst, write_reg_12_16, write_reg_17_21, mem_to_reg, incr_pc):
        self.incr_pc = incr_pc  
        self.reg_write = reg_write
        self.mem_read = mem_read
        self.mem_write = mem_write
        self.mem_to_reg = mem_to_reg
        
        if reg_dst == 0:  # If = 0; The register destination number for the Write register comes from the rt field (bits 20:16)
            self.write_reg = write_reg_12_16
        elif reg_dst == 1: # if = 1; The register destination number for the Write register comes from the rd field (bits 15:11)
            self.write_reg = write_reg_17_21
        else:   
            self.write_reg = 'X' # = junk

        if alu_op == 0b000010:  #(If R Type) (AKA if alu_op == 2)
            if function == 0b100000: # (If Add Instruction)
                self.alu_result = read_reg1_value + read_reg2_value  # ALUOutput <-- A op B
                self.sb_value = read_reg2_value # sb value = read_reg2 (reference handout)
            elif function == 0b100010: # (If Subtract Instrution)
                self.alu_result = read_reg1_value - read_reg2_value  # since subtract
                self.sb_value = read_reg2_value  # sb value = read reg2

        if alu_op == 0b000000: # (If I type)
            if opcode == 0b100000: #(If load byte instruction)
                self.alu_result = read_reg1_value + sign_offset
                self.sb_value = read_reg2_value
            elif opcode == 0b101000: # (If Store byte instruction)
                self.alu_result = read_reg1_value + sign_offset  # ALU adds reg1 and offset
                self.sb_value = read_reg2_value  # sb value = read reg2
                
    def clear(self):  # Reset values in ex_mem
        self.instruction_type = ""
        self.mem_read = 0
        self.mem_write = 0
        self.mem_to_reg = 0
        self.reg_write = 0
        self.read_reg1_value = 0
        self.read_reg2_value = 0
        self.WriteReg1 = 0
        self.WriteReg2 = 0
        self.sign_offset = 0
        self.alu_op = 0
        self.incr_pc = 0
        self.alu_result = 0
        self.sb_value = 0
        self.write_reg = 0
        self.function = 0
        
class Mem_wb_class:  

    def __init__(self):  # Constructor to initialize all MEM/WB values to zero.
        self.instruction_type = ""
        self.mem_to_reg = 0
        self.reg_write = 0
        self.mem_read = 0
        self.mem_write = 0
        self.reg_write = 0
        self.lb_value = 0
        self.alu_result = 0
        self.write_reg = 0


    def memory_read_write(self, mem_to_reg, reg_write, alu_result, write_reg, mem_read, sb_value, mem_write):
        self.mem_to_reg = mem_to_reg
        self.reg_write = reg_write
        self.alu_result = alu_result
        self.write_reg = write_reg

        if mem_read == 1 : #if mem_read asserted
            self.lb_value = main_mem[alu_result]  # load byte value comes from main menu (indexed via alu result)
        elif mem_write == 1:  # if mem_write asserted
            main_mem[alu_result] = sb_value  # store byte value is appended to main mem (indexed by the alu result)
        

                # Register[IR[15:11]] <-- ALUOutput

        
        
    def write_back(self):    

        if self.write_reg != "X":  #  if is junk
            if  self.mem_to_reg == 0 and self.mem_write == 0:  # and mem_to_reg and mem_write are both zero 
                regs[int(self.write_reg)] = self.alu_result  # 

            elif self.mem_write == 0 and self.mem_to_reg == 1: # load byte
                self.lb_value = main_mem[self.alu_result]  #  Result from ALU
                regs[int(self.write_reg)] = self.lb_value # lb value = regs          
                     
    def clear(self):  # Clears all values in the EX/MEM register
        
        self.alu_result = 0
        self.lb_value = 0
        self.instruction_type = ""
        self.mem_to_reg = 0
        self.reg_write = 0
        self.mem_read = 0
        self.mem_write = 0
        self.reg_write = 0
        self.write_reg = 0

        
def twos_comp(binary_input, length):  # Standard twos compliment converter (for SEOffset)
    if (binary_input & (1 << (length - 1))) != 0:
        binary_input = binary_input - (1 << length)
    return binary_input

    
def prime_main_mem():  # creates the main menu
    j = 0
    for x in range(0, main_mem_size):
        main_mem.append(j) 
        j += 1
        if j > main_mem_skip:
            j = 0
            
def prime_regs():  # Creates values for the 32 register (  format = 0xff + x)
    for x in range(0, 32):
        regs[x] = 256 + x

def bits1_32(hex_instruction):
    return ((hex_instruction & 0b11111111111111111111111111111111) >> 0)
    
def bits1_6(hex_instruction):
    return ((hex_instruction & 0b11111100000000000000000000000000) >>26)

def bits7_11(hex_instruction):
    return ((hex_instruction & 0b00000011111000000000000000000000) >>21)

def bits12_16(hex_instruction):
    return ((hex_instruction & 0b00000000000111110000000000000000) >>16)

def bits17_21(hex_instruction):
    return ((hex_instruction & 0b00000000000000001111100000000000) >>11)

def bits22_26(hex_instruction):
    return ((hex_instruction & 0b00000000000000000000011111000000) >> 6)
    
def bits27_32(hex_instruction):
    return ((hex_instruction & 0b00000000000000000000000000111111) >> 0)

def bits16_32(hex_instruction):
    return ((hex_instruction & 0b00000000000000001111111111111111) >> 0)

    

def print_regs():
    print '========================================================================================================================'
    print " Registers:"
    print '========================================================================================================================'
    for x in range (0, len(regs)):
        print " $" + str(x) + " = " + hex(regs[x])
    print '========================================================================================================================'    
    print '========================================================================================================================'


        

        
def print_out_everything():    # And now a really long print statement

    # A if block for zero displays needs to be provided for each read/write pair, is provided so that a blank set can be printed for the 0th cycle.  (Possible since all instances are initialized to zero)
    # Alternatively, instead of givng ifs blocks for each rzero case, we could also have given a print statement.


    print '------------------------------------------------------------------------------------------------------------------------'
    print ' [IF/ID Write: (Written to by the IF stage)]'
    print '------------------------------------------------------------------------------------------------------------------------'
    if if_id_copy.instruction == 0:
        print ' Control = 00000000'
    else:
        print ' Instruction = ' + hex(if_id_copy.instruction)
        print ' IncrPC = ' + hex(if_id_copy.incr_pc)
    print '------------------------------------------------------------------------------------------------------------------------'
    print ' [IF/ID Read: (Read to by the ID stage)]'
    print '------------------------------------------------------------------------------------------------------------------------'          
    if if_id_prime.instruction == 0:
        print ' Control = 00000000'
    else:    
        print ' Instruction = ' + hex(if_id_prime.instruction)
        print ' IncrPC = ' + hex(if_id_prime.incr_pc)
    print '========================================================================================================================'
    print
    print '========================================================================================================================'
    print '------------------------------------------------------------------------------------------------------------------------'
    print ' [ID/EX Write (Written to by the ID stage)]'
    print '------------------------------------------------------------------------------------------------------------------------'
    print ' Control: RegDst = ' + str(id_ex_copy.reg_dst) + ', ALUSrc = ' + str(id_ex_copy.alu_src) + ', ALUOp = ' + str(bin(id_ex_copy.alu_op)) + ', MemRead = ' + str(id_ex_copy.mem_read) + ', MemWrite = ' + str(id_ex_copy.mem_write) + ', MemToReg = ' + str(id_ex_copy.mem_to_reg) + ', RegWrite = ' + str(id_ex_copy.reg_write) 
    if id_ex_copy.instruction == 0:
        print ' IncrPC = 0'
    else:
        print ' IncrPC = '+ hex(id_ex_copy.incr_pc)
    print ' ReadReg1Value = '+ hex(id_ex_copy.read_reg1_value)
    print ' ReadReg2Value = '+ hex(id_ex_copy.read_reg2_value)
    if id_ex_copy.sign_offset == "X":
        print " SEOffset = " + "X"
    else:    
        print ' SEOffset = ' + str(id_ex_copy.sign_offset)
    print ' WriteReg_20_16 = '+ str(id_ex_copy.write_reg_12_16)
    print ' WriteReg_15_11 = '+ str(id_ex_copy.write_reg_17_21)
    if id_ex_copy.function == "X":
        print ' Function = X'
    else:
        print ' Function = ' + hex(id_ex_copy.function)
    print '------------------------------------------------------------------------------------------------------------------------'
    print ' [ID/EX Read (Read to by the EX stage)]'
    print '------------------------------------------------------------------------------------------------------------------------'
    print ' Control: RegDST = ' + str(id_ex_prime.reg_dst) + ', ALUSrc = ' + str(id_ex_prime.alu_src) + ', ALUOp = ' + str(bin(id_ex_prime.alu_op)) + ', MemRead = '+ str(id_ex_prime.mem_read) + ', MemWrite = ' + str(id_ex_prime.mem_write) + ', MemToReg = ' + str(id_ex_prime.mem_to_reg) + ', RegWrite = ' + str(id_ex_prime.reg_write) 
    if id_ex_prime.instruction == 0:
        print ' IncrPC = 0'
    else:
        print ' IncrPC =', str(id_ex_prime.incr_pc)        
    print ' ReadReg1Value = ' + hex(id_ex_prime.read_reg1_value)
    print ' ReadReg2Value = ' + hex(id_ex_prime.read_reg2_value)
    if id_ex_prime.sign_offset == "X":
        print " SEOffset =" + "X"
    else:
        print " SEOffset = " + str(id_ex_prime.sign_offset)
    print ' WriteReg_20_16 = ' + str(id_ex_prime.write_reg_12_16)
    print ' WriteReg_15_11 = ' + str(id_ex_prime.write_reg_17_21)
    if id_ex_prime.function == "X":
        print ' Function = X'
    else:
        print ' Function = '+ hex(id_ex_prime.function)
    print '========================================================================================================================'
    print
    print '========================================================================================================================'
    print '------------------------------------------------------------------------------------------------------------------------'
    print ' [EX/MEM Write (Written to by the EX stage)]'
    print '------------------------------------------------------------------------------------------------------------------------'
    print ' Control: MemRead = ' + str(ex_mem_copy.mem_read) + ', MemWrite = ' + str(ex_mem_copy.mem_write) + ', MemToReg = ' + str(ex_mem_copy.mem_to_reg) + ', RegWrite = ' + str(ex_mem_copy.reg_write) 
    print ' ALUResult = ' + hex(ex_mem_copy.alu_result)
    print ' SBValue = ' + hex(ex_mem_copy.sb_value)
    print ' WriteRegNum = ' + str(ex_mem_copy.write_reg)
    print '------------------------------------------------------------------------------------------------------------------------'
    print ' [EX/MEM READ (Read to by the MEM stage)]'
    print '------------------------------------------------------------------------------------------------------------------------'
    print ' Control: MemRead = ' + str(ex_mem_prime.mem_read) + ', MemWrite = ' + str(ex_mem_prime.mem_write) + ', MemToReg = '+ str(ex_mem_prime.mem_to_reg) + ', RegWrite = ' + str(ex_mem_prime.reg_write)
    print ' ALUResult = ' + hex(ex_mem_prime.alu_result)
    print ' SBValue = ' + hex(ex_mem_prime.sb_value)
    print ' WriteRegNum = ' + str(ex_mem_prime.write_reg)
    print '========================================================================================================================'
    print
    print '========================================================================================================================'
    print '------------------------------------------------------------------------------------------------------------------------'
    print ' [MEM/WB Write (Written to by the MEM stage)]'
    print '------------------------------------------------------------------------------------------------------------------------'
    print ' Control: MemToReg = ' + str(mem_wb_copy.mem_to_reg) + ', RegWrite = ' + str(mem_wb_copy.reg_write)
    print ' LBDataValue = ' + hex(mem_wb_copy.lb_value)
    print ' ALUResult = ' + hex(mem_wb_copy.alu_result)
    print ' WriteRegNum = ' + str(mem_wb_copy.write_reg)
    print'-------------------------------------------------------------------------------------------------------------------------'
    print ' [MEM/WB Read (Read by the WB stage)]'
    print'-------------------------------------------------------------------------------------------------------------------------'
    print ' Control: MemToReg = ' + str(mem_wb_prime.mem_to_reg) + ', RegWrite = ' + str(mem_wb_prime.reg_write) 
    print ' LBDataValue = ' + hex(mem_wb_prime.lb_value)
    print ' ALUResult = ' + hex(mem_wb_prime.alu_result)
    print ' WriteRegNum = ' + str(mem_wb_prime.write_reg)
    print '========================================================================================================================'
    print
    print_regs()  # print the registers (each time the print_out_everything function is called)
    print
    print
    print
    print
    print
    print
    
 
#   Functions are defined for each "stage" load the stages and call logic functions within each class
    
# Fetches the next instruction out of the instruction cache.  Puts it in the Write version of the IF/ID pipeline register.
    
def if_stage(instruction,address): 
    if_id_copy.instruction = instruction
    if_id_copy.incr_pc = address

# Reads an instruction from the read version of the IF/ID pipeline register, decodes, and writes the value to the write version of the ID/EX pipeline register.    
    
def id_stage(): 
    id_ex_copy.decode(if_id_prime.instruction, if_id_prime.incr_pc)

# Performs the requested instruction on the specific operands that are read out of the read version of the IDEX pipeline register, and writes the values to the write version of the EX/MEM pipeline register.    
    
def ex_stage():
    ex_mem_copy.execute(id_ex_prime.mem_read, id_ex_prime.mem_write, id_ex_prime.reg_write, id_ex_prime.alu_op, id_ex_prime.read_reg1_value, id_ex_prime.read_reg2_value, id_ex_prime.sign_offset, id_ex_prime.function, id_ex_prime.incr_pc, id_ex_prime.opcode, id_ex_prime.reg_dst, id_ex_prime.write_reg_12_16, id_ex_prime.write_reg_17_21, id_ex_prime.mem_to_reg, id_ex_prime.incr_pc)

#  If he instruction s an lb, then use the address calculated in the EX stage as an index into the main Memory array, otherwise just pass information from the read version of the EX/MEM pipeline to the write version of the MEM/WB.    
    
def mem_stage():
    mem_wb_copy.memory_read_write(ex_mem_prime.mem_to_reg, ex_mem_prime.reg_write, ex_mem_prime.alu_result, ex_mem_prime.write_reg, ex_mem_prime.mem_read, ex_mem_prime.sb_value,
                               ex_mem_prime.mem_write)

# Write to the registers based on information you read out of the Read version of the MEM/WB.
    
def wb_stage():
    mem_wb_prime.write_back()

if_id_copy = If_id_class(0, starting_address)
if_id_prime = If_id_class(0, 0)
id_ex_copy = Id_ex_class()
id_ex_prime = Id_ex_class()
ex_mem_copy = Ex_mem_class()
ex_mem_prime = Ex_mem_class()
mem_wb_copy = Mem_wb_class()
mem_wb_prime = Mem_wb_class()
       
def copy_write_to_read():
    
    global if_id_prime  # copy targets are global so they can re-instanciate each time (otherwise everything will be zero)
    global id_ex_prime
    global ex_mem_prime
    global mem_wb_prime
    if_id_prime = copy.copy(if_id_copy)
    id_ex_prime = copy.copy(id_ex_copy)
    ex_mem_prime = copy.copy(ex_mem_copy)
    mem_wb_prime  = copy.copy(mem_wb_copy)
    id_ex_copy.clear()  # Clear all values within each register.  (IF/ID not required, since they dont default to zero anyways)
    ex_mem_copy.clear()
    mem_wb_copy.clear()



# Main function, prints one loop of the print statement at null, then prints 12 loops of the print statement with their respective instructions as inputs.



def main_loop():
   
    prime_regs()
    prime_main_mem()
    print '[CLOCK CYCLE: 0]' 
    print_out_everything() 
    address = starting_address
    for x in range(0,len(instructions)): 
        print '========================================================================================================================'
        print '========================================================================================================================'
        print " [CLOCK CYCLE: " + str(x + 1) +']'
        instruction = instructions[x]
        if_stage(instruction, address)
        id_stage()
        ex_stage()
        mem_stage()
        wb_stage()
        print_out_everything()
        copy_write_to_read()
        address = address + 4

    

# Finally the main loop is called to execute the whole program.
        
main_loop()
    