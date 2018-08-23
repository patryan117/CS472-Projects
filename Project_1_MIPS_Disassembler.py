"""
Created on Sun Feb 12 11:51:29 2017

@author: Patrick Ryan
Class:  Computer Architecture
Language Python 2.7


Input an array of hex-instructions, and return a of decoded MIPS instructions (e.g. 7a078 ADD $2, $9, $8).
Instruction types de-constructed in this assignment are ADD, AND, OR, SLT, SUB, BEQ, BNE, LW, and SW.
"""

import numpy as np

hex_instructions = [0x022da822, 0x8ef30018, 0x12a70004, 0x02689820,
                    0xad930018, 0x02697824, 0xad8ffff4, 0x018c6020,
                    0x02a4a825, 0x158ffff6, 0x8ef9fff0]

# Vectorize hex_instructions as a numpy array so it can be printed in hex format

A = np.array(hex_instructions)
vhex = np.vectorize(hex)


def deconstruct(x):
    # Start the address at 4 less than the actual target address, since the PC  will be incremented at the begining of each loop iteration

    address = int("7a05c", 16)

    print
    print
    print
    "The entered hex instructions are :" + str(vhex(A))
    print
    print
    "---------------------------------------------------------------------"
    print
    "The deconstructed MIPS instructions are:"
    print
    "---------------------------------------------------------------------"
    print

    instruction = 0

    for x in hex_instructions:

        opcode = 0
        address += 4  # Increment the PC address for each entry (Branchse are assumed to fail)

        """The for loop will pass each 32-bit instruction through a series of bitwise & maskes that
        will isolate a given range. A shift will follow each range-set"""

        bits1_32 = bin((x & 0b1111111111111111111111111111111))
        bits1_6 = bin((x & 0b11111100000000000000000000000000) >> 26)
        bits7_11 = bin((x & 0b00000011111000000000000000000000) >> 21)
        bits12_16 = bin((x & 0b00000000000111110000000000000000) >> 16)
        bits17_21 = bin((x & 0b00000000000000001111100000000000) >> 11)
        bits22_26 = bin((x & 0b00000000000000000000011111000000) >> 6)
        bits27_32 = bin((x & 0b00000000000000000000000000111111) >> 0)
        bits17_32 = bin((x & 0b00000000000000001111111111111111) >> 0)
        bit17 = bin((x & 0b00000000000000001000000000000000) >> 15)

        """A block of if statements conditionally identify each instruction type, by evaluating the contents
        of specific bitfields.  The first 5 instruction types (ADD, AND, OR, SLT AND SUB) are evaluated by """

        if bits1_6 == "0b0" and bits27_32 == "0b100000":
            opcode = "ADD"
        elif bits1_6 == "0b0" and bits27_32 == "0b100100":
            opcode = "AND"
        elif bits1_6 == "0b0" and bits27_32 == "0b100101":
            opcode = "OR"
        elif bits1_6 == "0b0" and bits27_32 == "0b101010":
            opcode = "SLT"
        elif bits1_6 == "0b0" and bits27_32 == "0b100010":
            opcode = "SUB"
        elif bits1_6 == "0b100":
            opcode = "BEQ"
        elif bits1_6 == "0b101":
            opcode = "BNE"
        elif bits1_6 == "0b100011":
            opcode = "LW"
        elif bits1_6 == "0b101011":
            opcode = "SW"
        else:
            print
            "No opcode found"

        """Once an instruction type has been identified, the bitfields will be used construct an assembly
        instruction. Each instruction's rs, rt, rd and offset is isolated according to its instruction
        type, and using these binary values, an instruction type will be formed using concatenated strings"""

        if opcode == "ADD":
            rs = bits7_11
            rt = bits12_16
            rd = bits17_21
            x = bits22_26
            offset = 0
            func = bits27_32
            instruction = format(address, '02x') + ": " + str(opcode) + " $" + str(int(rd, 2)) + ", " + "$" + str(
                int(rs, 2)) + ", " + "$" + str(int(rt, 2))

        elif opcode == "AND":
            rs = bits7_11
            rt = bits12_16
            rd = bits17_21
            x = bits22_26
            offset = 0
            func = bits27_32
            instruction = format(address, '02x') + ": " + str(opcode) + " $" + str(int(rd, 2)) + ", " + "$" + str(
                int(rs, 2)) + ", " + "$" + str(int(rt, 2))

        elif opcode == "OR":
            rs = bits7_11
            rt = bits12_16
            rd = bits17_21
            x = bits22_26
            offset = 0
            func = bits27_32
            instruction = format(address, '02x') + ": " + str(opcode) + " $" + str(int(rd, 2)) + ", " + "$" + str(
                int(rs, 2)) + ", " + "$" + str(int(rt, 2))

        elif opcode == "SLT":
            rs = bits7_11
            rt = bits12_16
            rd = bits17_21
            x = bits22_26
            offset = 0
            func = bits27_32
            instruction = format(address, '02x') + ": " + str(opcode) + " $" + str(int(rd, 2)) + ", " + "$" + str(
                int(rs, 2)) + ", " + "$" + str(int(rt, 2))

        elif opcode == "SUB":
            rs = bits7_11
            rt = bits12_16
            rd = bits17_21
            x = bits22_26
            offset = 0
            func = bits27_32
            instruction = format(address, '02x') + ": " + str(opcode) + " $" + str(int(rd, 2)) + ", " + "$" + str(
                int(rs, 2)) + ", " + "$" + str(int(rt, 2))

        elif opcode == "BEQ":
            rs = bits7_11
            rt = bits12_16
            offset = int(bits17_32, 2)

            if bit17 == '0b1':
                mask = 2 ** ((len((offset)[2:])) - 1)
                offset = -(int(offset, 2) & mask) + (int(offset, 2) & ~mask)
                new_address = (address) + (offset * 4)
                instruction = format(address, '02x') + ": " + str(opcode) + " $" + str(int(rs, 2)) + ", " + "$" + str(
                    int(rt, 2)) + ", " + format(new_address, '02x')
            else:
                new_address = (address) + (offset * 4)
                instruction = format(address, '02x') + ": " + str(opcode) + " $" + str(int(rs, 2)) + ", " + "$" + str(
                    int(rt, 2)) + ", " + format(new_address, '02x')

        elif opcode == "BNE":
            rs = bits7_11
            rt = bits12_16
            offset = bits17_32
            if bit17 == '0b1':
                mask = 2 ** ((len((offset)[2:])) - 1)
                offset = -(int(offset, 2) & mask) + (int(offset, 2) & ~mask)
                new_address = (address) + (offset * 4)
                instruction = format(address, '02x') + ": " + str(opcode) + " $" + str(int(rs, 2)) + ", " + "$" + str(
                    int(rt, 2)) + ", " + format(new_address, '02x')
            else:
                instruction = format(address, '02x') + ": " + str(opcode) + " $" + str(int(rs, 2)) + ", " + "$" + str(
                    int(rt, 2)) + ", " + format(new_address, '02x')
                new_address = (address) + (offset * 4)


        elif opcode == "LW":
            rs = bits7_11
            rt = bits12_16
            offset = bits17_32
            if bit17 == '0b1':
                mask = 2 ** ((len((offset)[2:])) - 1)
                offset = -(int(offset, 2) & mask) + (int(offset, 2) & ~mask)
                instruction = format(address, '02x') + ": " + str(opcode) + " $" + str(int(rt, 2)) + ", " + str(
                    offset) + ", " + "(" + str(int(rs, 2)) + ")"
            else:
                instruction = format(address, '02x') + ": " + str(opcode) + " $" + str(int(rt, 2)) + ", " + str(
                    int(offset, 2)) + ", " + "(" + str(int(rs, 2)) + ")"


        elif opcode == "SW":
            rs = bits7_11
            rt = bits12_16
            offset = bits17_32
            if bit17 == '0b1':
                mask = 2 ** ((len((offset)[2:])) - 1)
                offset = -(int(offset, 2) & mask) + (int(offset, 2) & ~mask)
                instruction = format(address, '02x') + ": " + str(opcode) + " $" + str(int(rt, 2)) + ", " + str(
                    offset) + ", " + "(" + str(int(rs, 2)) + ")"
            else:
                instruction = format(address, '02x') + ": " + str(opcode) + " $" + str(int(rt, 2)) + ", " + str(
                    int(offset, 2)) + ", " + "(" + str(int(rs, 2)) + ")"

        """A print instruction set within the for loop will print out the assembly instruction produced by
        each iteration through the hex_instructions list.  As currently set, the list will only print out the
        compiled instruction for each hex input, however un-quoting the
          """

        print
        instruction

        # Unquote the print block belowhere to enable troubleshooting (showing bit fields after each instruction)
        """
        print  "--------------------------------------------------------------"
        print "Address :" + format(address, '02x')
        print "bits 1:32  = " + bits1_32
        print "bits 1:6   = " + bits1_6
        print "bits 7:11  = " + bits7_11
        print "bits 12:16 = " + bits12_16
        print "bits 17:21 = " + bits17_21
        print "bits 22:26 = " + bits22_26
        print "bits 27:32 = " + bits27_32
        print "bits 17:32 = " + bits17_32
        print "bit 17 ="  + bit17
        print "offset = " + str(offset)
        print type(offset)
        print  "--------------------------------------------------------------"
        """

    # Calling the function on the hex_instructions list will execute the defined program.


deconstruct(hex_instructions)