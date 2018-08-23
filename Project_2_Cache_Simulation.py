
"""
Created on Sun Feb 12 11:51:29 2017

Author: Patrick Ryan
Class:  Computer Architecture
Language Python 2.7

Program summary: Emulates a direct mapped cache by controling reads and writes
between a two dimensional array (cache) and a one dimensional array (main memory).  
""" 

import pandas as pd
import numpy as np




# Define a function which uses binary masking to isolate each hex digit and
# use for indexing.  Each must be declared as a global variable


def convert(address):
    
    global hexall        # (1/2/3)
    global hex1          # (1/_/_)
    global hex2          # (_/2/3)
    global hex3          # (_/_/3)
    global hex2_3        # (_/2/3)
    global hex1_2plus0   # (1/2/0)
    global hex2plus0     # (_/2/0)
    
    hexall      = ((address & 0b111111111111) >> 0)
    hex1        = ((address & 0b111100000000) >> 8)
    hex2        = ((address & 0b000011110000) >> 4)
    hex3        = ((address & 0b000000001111) >> 0)
    hex2_3      = ((address & 0b000011111111) >> 0)
    hex1_2plus0 = ((address & 0b111111110000) >> 0)  
    hex2plus0   = ((address & 0b000011110000) >> 0)  

readcommandhex = "" 


cache_length = 0x10  #cache length = 16
mm_length = 0xff # Main memory length = 255 

cache = np.zeros((cache_length, 19), dtype=int)  #  Initialize the cache with zeroes using numpy. (16 x (16 + 3)(+ 3 for valid, tag and slot columns))
cache_column_labels = ['Slot', 'Valid', 'Tag', 'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12', 'D13', 'D14', 'D15']  # Designate lables for the each of the 19 columns

mm = []
cache_row_labels = []  # Initialize row lables (created in the following for loop)
cache_slots = []




for k in range (cache_length):  # For loop which names the row lables and populates the slot lables 
    j = ("")
    cache_row_labels.append(j)
    cache_slots.append(k)
 
for x in range (100):       #  Initalizes the Main Memory array (stacking x1 - xff on top of each other 10 times)    
    for k in range (mm_length +1):
        mm.append(k)
        
vhex = np.vectorize(hex)   # Create a vectorizing function which will allow the cache to be printed in hex format.
cache[:,0] = cache_slots   #  Set the cache slot column (col 1) to the list created in the first for loop (x0 - xe)    

prompt = 0    # Initalize prompt and command (which will be to store raw data, input by the user)
command = 0




# Use a while loop to keep cache program cycling (quits when user returns "Q".)
# (Using the upper method allows the user to input their response in either uppercase or lowercase)

while (prompt != "Q"):
    print
    prompt = (str(raw_input("Please enter a command: \n\n  (W): Write Cache \n  (R): Read Cache\n  (D): Display Cache \n  (Q): Quit Program \n \n>>").upper()))
    print
    print
    
    # Write Command
    
    if prompt == "W":
        print "Value entered: " + prompt
        write_address = raw_input("What address would you like to write to?:  ")
        print
        write_address_hex = int(write_address,16)
        convert(write_address_hex)   
        print "At location (" + str(write_address) + ") the value is: " + hex(cache[hex2][hex3+3]) 
        print
        write_data = raw_input("What data would you like to write to that address?:  ")
        write_data_hex = int(write_data,16)             
        print
                
        print "The value " + hex(write_data_hex) + " has been written to address " + hex(write_address_hex)
        print
         
        
        # If data is in the requested address & tag matches & valid bit == 1 then hit, if not, miss and
        # update address in MM, copy the block into cache, and change valid bit/tag.
           
        if cache[hex2][hex3+3] == write_data_hex and cache[hex2][2] == hex1 and cache[hex2][1] == 1 :
            print"Cache Hit."
            
        elif cache[hex2][hex3] != write_data_hex:
            print "Cache miss."
            mm[write_address_hex] = write_data_hex
                        
            for x in range(16): 
                cache[hex2][1] = 1
                cache[hex2][2] = hex1
                mm[write_address_hex] = write_data_hex 
                cache[hex2][3+x] = mm[(hex1_2plus0) + x]

    # Read Command
    # If the requested read matches the value expected, then cache hit.  Otherwise cache miss
    # and the appropriate block is copied in from mm to 
               
                
    if prompt == "R":  #Read command 
        print "Value entered: " + prompt
        print
        read_command = raw_input("What address would you like to read?: ")
        print
        read_command_hex = int(read_command,16)
        convert(read_command_hex)    
        print "At location (" + hex(read_command_hex) + ") the value is: " + hex(cache[hex2][hex3+3]) 
        print
                  
        if cache[hex2][hex3+3] == (hex2plus0+hex3) and cache[hex2][2] == hex1 and cache[hex2][1] == 1 :
            print"Cache Hit."
            
        if cache[hex2][hex3+3] != (hex2plus0+hex3) or cache[hex2][2] != hex1 or cache[hex2][1] != 1:
            print "Cache Miss."
            
            for x in range(16): 
                cache[hex2][1] = 1  # change valid bit to 1
                cache[hex2][2] = hex1  # change tag to second 
                cache[hex2][3+x] = mm[(hex1_2plus0) + x]  # fill cache with 16 values()
          
     
        # Display the current state of cache.
                    
    if prompt == "D":
        print "Value entered: " + prompt
        print
        print pd.DataFrame(vhex(cache), columns=cache_column_labels, index=cache_row_labels)

        #  Quit the program.
    
    if prompt == "Q":
        print "Exiting Program..."
        break
        
        # If the user enters anything other than D, W, R or Q, then the prompt is re-iterated.
    
    
    elif prompt != "D" and prompt != "W" and prompt != "R" and prompt != "Q":
        print "Invalid response, plese try another command: "
        
        
        

        




