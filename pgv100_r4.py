import serial
import time

# Replace with the correct port and baudrate
port = 'COM6'
baudrate = 112500  # Adjust this to match your device's settings


# Open the serial port
ser = serial.Serial(port, baudrate, timeout=10)

# The two bytes to be sent
# follow left-hand lane"0xE8,0x17" follow right-hand lane: "0xE4,0x1B", Straight aheat: "0xEC,0x13", No lane is selected error code5: "0xE0, 0x1F"
# request Telegram: "0xC8,0x37"
byte1 = "C8"
byte2 = "37"

byte1 = bytes.fromhex(byte1)
byte2 = bytes.fromhex(byte2)


def twos_complement_to_decimal(binary_str):
    n = len(binary_str)
    
    # Check if the number is negative
    if binary_str[0] == '1':
        # Invert all bits
        inverted_bits = ''.join('1' if bit == '0' else '0' for bit in binary_str)
        # Convert inverted binary to decimal and add 1
        decimal = int(inverted_bits, 2) + 1
        # Make it negative
        decimal = -decimal
    else:
        # Convert directly to decimal
        decimal = int(binary_str, 2)
    
    return decimal

# Function to send two bytes to the serial port and print the response
def send_bytes_to_serial(port, baudrate, byte1, byte2):
    try:                  
        # Send the two bytes to the serial port
        ser.write(byte1)
        ser.write(byte2)
        print(f"Sent: {byte1.hex().upper()} {byte2.hex().upper()}")

        # Give the device some time to process the command
        time.sleep(1)

        # Read the response from the serial port
        response = ser.read(ser.in_waiting or 1)  # Read all available bytes
        # while ser.in_waiting > 
        # response = ser.read(ser.in_waiting)
        response_hex = response.hex().upper()  # Convert the response to a hex string
        byte_1 = bin(response[0])[2:].zfill(8)
        byte_2 = bin(response[1])[2:].zfill(8)

        # response data
        ERR = byte_1[7]
        NP = byte_1[6]
        WRN = byte_1[5]
        CC1 = byte_1[4]
        A0 = byte_1[3]
        A1 = byte_1[2]
        CC2 = byte_1[1]

        RL = byte_2[7]
        LL = byte_2[6]
        NL = byte_2[5]
        RP = byte_2[4]
        LC0 = byte_2[3]
        LC1 = byte_2[2]
        TAG_NO = byte_2[1]
        
        # position data interpret       
        XPS = (response[2]*(128**3) + response[3]*(128**2) + response[4]*(128**1) + response[5])
        XPS_signed = twos_complement_to_decimal(bin(XPS)[2:].zfill(24))
        YPS = (response[6]*(128**1) + response[7])
        YPS_signed = twos_complement_to_decimal(bin(YPS)[2:].zfill(14))
        ANG = (response[10]*(128**1) + response[11]) 
        WRN_MSG = (response[18]*(128**1) + response[19]) 

        if TAG_NO == '1':
            TAG = (response[14]*(128**3) + response[15]*(128**2) + response[16]*(128**1) + response[17])
            TAG_CC1 = 0
            TAG_CC2 = 0
        else:    
            if CC1 == '1' or CC2 == '1':
                TAG_CC1 = (response[14]*(128**1) + response[15]) & 1023
                TAG_CC2 = (response[16]*(128**1) + response[17]) & 1023
                TAG = 0
            else:
                TAG_CC1 = 0
                TAG_CC2 = 0
                TAG = 0

        # print data
        print(f"Received: {response_hex}")
        
        print (f"ERR: {ERR}")
        print (f"NP: {NP}")
        print (f"WRN: {WRN}")
        print (f"CC1: {CC1}")
        print (f"A0: {A0}")
        print (f"A1: {A1}")
        print (f"CC2: {CC2}")

        print (f"RL: {RL}")
        print (f"LL: {LL}")
        print (f"NL: {NL}")
        print (f"RP: {RP}")
        print (f"LC0: {LC0}")
        print (f"LC1: {LC1}")
        print (f"TAG: {TAG_NO}")       

        print ('data interpret:')
        print (f"XOS_signed: {XPS_signed}")
        print (f"YOS_signed: {YPS_signed}")
        print (f"ANG: {ANG}")
        print (f"Data Matrix Tag No.: {TAG}")
        print (f"Control Code 1: {TAG_CC1}")
        print (f"Control Code 2: {TAG_CC2}")
        print (f"Warining Message: {bin(WRN_MSG)[2:].zfill(16)}")

    except serial.SerialException as e:
        print(f"Error: {e}")

# Send the bytes and print the response
while True:
    send_bytes_to_serial(port, baudrate, byte1, byte2)