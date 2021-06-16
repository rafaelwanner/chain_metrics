import plyvel
import sys
from binascii import hexlify, unhexlify



KEY = bytearray(b'43')
CHAINSTATE_DIR = "../../../../../media/rwanner/Samsung_T5/chainstate"



def reverse(h):
    byte_array = bytearray(h)
    h_new = bytearray(b'0')
    for i in range(0,len(byte_array),2):
        h_new[i:i+1] = byte_array[len(byte_array)-1-i-1], byte_array[len(byte_array)-1-i]
        
    return h_new



def encodeVarInt(h):
    n = int.from_bytes(unhexlify(h), byteorder='little')
    l = 0
    tmp = []
    data = ""
    while True:
        tmp.append(n & 0x7F)
        if l != 0:
            tmp[l] |= 0x80
        if n <= 0x7F:
            break
        n = (n >> 7) - 1
        l += 1

    tmp.reverse()
    for i in tmp:
        data += format(i, '02x')
    return bytearray(data, 'utf-8')



def decodeVarInt(data):
    n = 0
    i = 0
    while True:
        d = int(data[2 * i:2 * i + 2], 16)
        n = n << 7 | d & 0x7F
        if d & 0x80:
            n += 1
            i += 1
        else:
            return n



def deobfuscate(value, obfuscation_key):
    l_value = len(value)
    l_obf = len(obfuscation_key)

    #Extend the key to the same length as the value
    if l_obf < l_value:
        extended_key = (obfuscation_key * (int(l_value / l_obf) + 1))[:l_value]
    else:
        extended_key = obfuscation_key[:l_value]
    
    return format(int(value, 16) ^ int(extended_key, 16), 'x').zfill(l_value)



def parse_value(value):
    pass




def main():
    outpointTXID = bytearray(sys.argv[1], 'utf-8')      #input is hexlified 
    outpointIndex = bytearray(sys.argv[2], 'utf-8')     #ex: dec: 1 --> hex: 01 00 00 00

    needle = KEY + outpointTXID + encodeVarInt(outpointIndex)
    print(needle)

    try:
        db = plyvel.DB(CHAINSTATE_DIR, compression=None)
    except Exception as e:
        print("Exception: {}".format(e))
        return "Error occured!"

    #Read the obfuscation key from the database
    obfuscation_key = db.get(unhexlify(b'0e006f62667573636174655f6b6579'))
    obfuscation_key = hexlify(obfuscation_key)[2:]

    target_key = None
    target_value = None
    for key, value in db.iterator(prefix=unhexlify(needle)):
        target_key = hexlify(key)
        target_value = hexlify(value)
        break


    if target_value:
        deobfuscated_value = deobfuscate(target_value, obfuscation_key)
        utxo_data = parse_value(deobfuscated_value, target_key)

        return utxo_data

    else:
        return "Not a valid UTXO!"


if __name__ == "__main__":
    data = main()
    print(data)