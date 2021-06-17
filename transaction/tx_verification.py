import sys
from binascii import hexlify, unhexlify
import struct

sys.path.append('../')  

from chainstate.utxo_data import utxo_data
from transaction.script_engine import ScriptEngine
from transaction.script import assembleScript


def readIntLittleEndian(input):
    return struct.pack(">I", struct.unpack("<I", unhexlify(input[:8]))[0]), input[8:]


def readShortLittleEndian(input):
    return struct.pack(">H", struct.unpack("<H", unhexlify(input[:4]))[0]), input[4:]


def readLongLittleEndian(input):
    return struct.pack(">Q", struct.unpack("<Q", unhexlify(input[:16]))[0]), input[16:]


def readVarInt(input):
    varInt = ord(unhexlify(input[:2]))
    input = input[2:]
    returnInt = 0
    if varInt < 0xfd:
        return varInt, input
    if varInt == 0xfd:
          returnInt, input = readShortLittleEndian(input)
    if varInt == 0xfe:
        returnInt, input = readIntLittleEndian(input)
    if varInt == 0xff:
        returnInt, input = readLongLittleEndian(input)
    return int(hexlify(returnInt), 16), input


def fetchScript(input):
    outpointTXID = input[:64]
    outpointIndex = input[64:72]
    #input = input[72:]
    scriptLength, input = readVarInt(input[72:])
    unlockingScript = input[:2*scriptLength]
    #input = input[scriptLength:]
    seqNo, input = readIntLittleEndian(input[2*scriptLength:])

    data = utxo_data(outpointTXID, outpointIndex)

    return {
                'unlockingScript':     unlockingScript,
                'lockingScriptData':   data['scriptData'],
                'lockingScriptType':   data['scriptType']
            }, input      



def get_scripts(transaction):
    scripts = []
    version, transaction = readIntLittleEndian(transaction)
    inputCount, transaction = readVarInt(transaction)
    
    for inputIndex in range(0, inputCount):
        scriptData, transaction = fetchScript(transaction)
        unlocking, locking = assembleScript(scriptData)
        scripts.append([unlocking, locking])

    return scripts

    

def tx_verification(transaction):
    
    scripts = get_scripts(bytearray(transaction, 'utf-8'))
    return scripts
    """ TODO: Write script exection
    engine = ScriptEngine()
    for script in scripts:
        engine.load(script)
        res = engine.execute()
        if not res:
            return False

    return True
    """

if __name__ == "__main__":  
    
    transaction = sys.argv[1]

    res = tx_verification(transaction)
    print(res)