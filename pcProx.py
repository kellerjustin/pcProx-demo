
#
# pcProx Reader Demo with Python by Sawahashi
#
# Required: Python > 3, libusb
#
# Should work on Windows and Linux
# You may need to change VENDER_ID and PRODUCT_ID corresponding to your reader model
# JRK 2018-01-31 - forked/modified code to accommodate the reader config I use,
# and the 26-bit cards
# Returning the Facility Access code and number in a tuple

import usb.core
import usb.util
import time

def binToInt(binary):
    decimal = 0
    for digit in binary:
        decimal = decimal*2 + int(digit)
    return decimal

def getProx():
    ### CONFIG
    ### You may need to change VENDER_ID and PRODUCT_ID corresponding to a reader model
    ### JRK - changed PROX_END to 4
    VENDER_ID = 0x0C27
    PRODUCT_ID = 0x3BFA
    PROX_END = 4
    INTERFACE = 0

    # Detect the device
    dev = usb.core.find(idVendor=VENDER_ID, idProduct=PRODUCT_ID)
    if dev is None:
        raise ValueError('Card reader is not connected')

    # Make sure libusb handles the device
    if dev.is_kernel_driver_active(INTERFACE):
        print('Detach Kernel Driver')
        dev.detach_kernel_driver(INTERFACE)

    # Set a mode
    # ctrl_transfer is used to control endpoint0
    dev.set_configuration(1)
    usb.util.claim_interface(dev, INTERFACE)
    dev.ctrl_transfer(0x21, 9, 0x0300, 0, [0x008d])

    # Pull the status
    output = dev.ctrl_transfer(0xA1, 1, 0x0300, 0, PROX_END)

    # Convert output into integers
    proxHex = '0x'
    for h in (reversed(output)):
        #JRK - added if statement to handle 1-digit numbers without leading 0
        if (h < 16 and h > 0):
            proxHex += '0' + hex(h)[2:]
        else:
            proxHex += hex(h)[2:]
    #Get 24-digit binary (slice the first 2 and last 1 digit from the binary)
    b = (bin(int(proxHex, 16))[4:-1])
    '''
    Get Facility Access Code by slicing the first 8 binary digits and
    converting to integer. Then get the Card ID Number by converting the
    last 16 digits to integer
    '''
    fac = binToInt(b[:7])
    idNum = binToInt(b[-16:])
    '''
    #Print stmts for testing
    print(proxHex)
    print("Facility code: %s" % fac)
    print("ID Number: %s" % idNum)
    '''
    #Return a tuple with the fac and ID
    return(fac,idNum)


### Main Loop

prev = 0
print('Ready for Scan...')

while 1:
    result = getProx()
    if(result != prev):
        if(result[0] != 0):
            print(result)
        prev = result

    time.sleep(0.3);
