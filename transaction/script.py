import sys

from utils.keys import uncompressPublicKey

def assembleScript(scriptData):
    type = scriptData['lockingScriptType']
    lockingScriptData = scriptData['lockingScriptData']

    if type == 0x00:
        lockingScript =  bytearray('76', 'utf-8') + bytearray('A9', 'utf-8') + bytearray('14', 'utf-8') \
                        + lockingScriptData + bytearray('88', 'utf-8') + bytearray('AC', 'utf-8')
    
    elif type == 0x01:
        lockingScript = bytearray('A9', 'utf-8') + bytearray('14', 'utf-8') + lockingScriptData + bytearray('87', 'utf-8')
    
    elif type <= 0x05:
        lockingScript = uncompressPublicKey(bytearray(type) + lockingScriptData) + bytearray('87', 'utf-8')

    else:
        lockingScript = scriptData


    return lockingScript


if __name__=="__main__":

    input = {'unlockingScript': bytearray(b'47304402201027b396c891c7df0f4104936ce4601afd7d0e4acdd2525cc091b307835b49a60220723ec95a4ae204a82060b90744b8'), 
    'lockingScriptData': bytearray(b'd9eee13f3a6f05f070c2e7e02d22f8af71983c15'), 'lockingScriptType': 0}
    res = assembleScript(input)
    print(res)
