import plyvel
import sys
from binascii import hexlify, unhexlify
import base58



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


def parseVarInt(value, offset=0):

    data = value[offset:offset+2]
    offset += 2
    more_bytes = int(data, 16) & 0x80
    while more_bytes:
        data += value[offset:offset+2]
        more_bytes = int(value[offset:offset+2], 16) & 0x80
        offset += 2

    return data, offset



def deobfuscate(value, obfuscation_key):
    l_value = len(value)
    l_obf = len(obfuscation_key)

    #Extend the key to the same length as the value
    if l_obf < l_value:
        extended_key = (obfuscation_key * (int(l_value / l_obf) + 1))[:l_value]
    else:
        extended_key = obfuscation_key[:l_value]
    
    return bytearray(format(int(value, 16) ^ int(extended_key, 16), 'x').zfill(l_value), 'utf-8')


def decompress(value):

    if value == 0:
        return 0
    value -= 1
    e = value % 10
    value /= 10
    if e < 9:
        d = (value % 9) + 1
        value /= 9
        n = value * 10 + d
    else:
        n = value + 1
    while e > 0:
        n *= 10
        e -= 1
    return n



def parse_value(key, value):
    
    tx_id = key[2:66]
    tx_index = decodeVarInt(key[66:])

    #Block height and coinbase
    height, offset = parseVarInt(value)
    height = decodeVarInt(height) >> 1
    coinbase = height & 0x01

    #Amount of satoshis available
    amount, offset = parseVarInt(value, offset)
    amount = decompress(decodeVarInt(amount))

    #Script type
    script_type, offset = parseVarInt(value, offset)
    script_type = decodeVarInt(script_type)

    if script_type <= 0x02:     #P2PKH (0x01) or P2PH (0x02)
        script_size = 40        #script only contains a bitcoin address (20 bytes)
    
    elif script_type <= 0x05:   #P2PK 
        script_size = 64        #script only contains a public key (32 bytes)
        script_size += 2        #include script_type byte
        offset -= 2
    
    else:                       #script stored in full (special script)
        nspecialscripts = 6
        script_size = (script_type - nspecialscripts) * 2
    
    script = value[offset:]

    if script_size != len(script):
        print("Wrong script size!")
        return 0

    return {    
                'TXID': tx_id, 
                'TX Index': tx_index, 
                'height': height, 
                'coinbase': coinbase, 
                'amount': amount, 
                'script_type': script_type, 
                'script_data': script
            }




def utxo_data():
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
        utxo_data = parse_value(target_key, deobfuscated_value)

        return utxo_data

    else:
        return "Not a valid UTXO!"


if __name__ == "__main__":
    data = utxo_data()
    print(data)