import numpy as np
import binascii
import hashlib
import base58
import struct
import datetime
import hashlib


def reverse(h):
    byte_array = bytearray(h)
    h_new = bytearray(b'0')
    for i in range(0,len(byte_array),2):
        h_new[i:i+1] = byte_array[len(byte_array)-1-i-1], byte_array[len(byte_array)-1-i]
        
    return bytes(h_new)


def stringLittleEndianToBigEndian(string):
    string = binascii.hexlify(string)
    n = len(string) / 2
    fmt = '%dh' % n
    return struct.pack(fmt, *reversed(struct.unpack(fmt, string)))


def readIntLittleEndian(blockFile):
    return struct.pack(">I", struct.unpack("<I", blockFile.read(4))[0])


def readShortLittleEndian(blockFile):
    return struct.pack(">H", struct.unpack("<H", blockFile.read(2))[0])


def readLongLittleEndian(blockFile):
    return struct.pack(">Q", struct.unpack("<Q", blockFile.read(8))[0])


def hexToInt(value):
    return int(binascii.hexlify(value), 16)


def hexToStr(value):
    return binascii.hexlify(value)


def readVarInt(blockFile):
    varInt = ord(blockFile.read(1))
    returnInt = 0
    if varInt < 0xfd:
        return varInt
    if varInt == 0xfd:
          returnInt = readShortLittleEndian(blockFile)
    if varInt == 0xfe:
        returnInt = readIntLittleEndian(blockFile)
    if varInt == 0xff:
        returnInt = readLongLittleEndian(blockFile)
    return int(binascii.hexlify(returnInt), 16)


def readInput(blockFile):
    previousHash = binascii.hexlify(blockFile.read(32)[::-1])
    outId = binascii.hexlify(blockFile.read(4))
    scriptLength = readVarInt(blockFile)
    scriptSignatureRaw = hexToStr(blockFile.read(scriptLength))
    scriptSignature = scriptSignatureRaw
    seqNo = binascii.hexlify(readIntLittleEndian(blockFile))

    print("\n" + "Input")
    print("-" * 20)
    print("> Previous Hash: ", previousHash)
    print("> Out ID: ", outId)
    print("> Script length: " + str(scriptLength))
    print("> Script Signature (PubKey) Raw: ", scriptSignatureRaw)
    print("> Script Signature (PubKey): ", scriptSignature)
    print("> Seq No: ", seqNo)


def readOutput(blockFile):
    value = hexToInt(readLongLittleEndian(blockFile)) / 100000000.0
    scriptLength = readVarInt(blockFile)
    scriptSignatureRaw = hexToStr(blockFile.read(scriptLength))
    scriptSignature = scriptSignatureRaw
    address = ''
    try:
        address = publicKeyDecode(scriptSignature)
    except:
        address = ''
  
    print("\n" + "Output")
    print("-" * 20)
    print("> Value: " + str(value))
    print("> Script length: " + str(scriptLength))
    print("> Script Signature (PubKey) Raw: ", scriptSignatureRaw)
    print("> Script Signature (PubKey): ", scriptSignature)
    print("> Address: ", address)


def readTransaction(blockFile):
    extendedFormat = False
    beginByte = blockFile.tell()
    inputIds = []
    outputIds = []
    version = hexToInt(readIntLittleEndian(blockFile)) 
    cutStart1 = blockFile.tell()
    cutEnd1 = 0
    inputCount = readVarInt(blockFile)
    
    print("\n\n" + "Transaction")
    print("-" * 100)
    print("Version: " + str(version))
    
    print("\nInput Count: " + str(inputCount))
    for inputIndex in range(0, inputCount):
        inputIds.append(readInput(blockFile))
    outputCount = readVarInt(blockFile)
    print("\nOutput Count: " + str(outputCount))
    for outputIndex in range(0, outputCount):
        outputIds.append(readOutput(blockFile))
        
    lockTime = hexToInt(readIntLittleEndian(blockFile))
    if lockTime < 500000000:
        print("\nLock Time is Block Height: " + str(lockTime))
    else:
        print("\nLock Time is Timestamp: " + datetime.datetime.fromtimestamp(lockTime).strftime('%d.%m.%Y %H:%M'))


def startsWithOpNCode(pub):
  try:
    intValue = int(pub[0:2], 16)
    if intValue >= 1 and intValue <= 75:
      return True
  except:
    pass
  return False


def publicKeyDecode(pub):
    if pub.lower().startswith(b'76a914'):
        pub = pub[6:-4]
        result = (b'\x00') + binascii.unhexlify(pub)
        h5 = hashlib.sha256(result)
        h6 = hashlib.sha256(h5.digest())
        result += h6.digest()[:4]
        return base58.b58encode(result)
    elif pub.lower().startswith(b'a9'):
        return ""
    elif startsWithOpNCode(pub):
        pub = pub[2:-2]
        h3 = hashlib.sha256(binascii.unhexlify(pub))
        h4 = hashlib.new('ripemd160', h3.digest())
        result = (b'\x00') + h4.digest()
        h5 = hashlib.sha256(result)
        h6 = hashlib.sha256(h5.digest())
        result += h6.digest()[:4]
        return base58.b58encode(result)
    return ""


def process_block(blockFile):
    magicNumber = binascii.hexlify(blockFile.read(4))
    blockSize = hexToInt(readIntLittleEndian(blockFile))
    version = hexToInt(readIntLittleEndian(blockFile))
    previousHash = reverse(binascii.hexlify(blockFile.read(32)))
    merkleHash = reverse(binascii.hexlify(blockFile.read(32)))
    creationTimeTimestamp = hexToInt(readIntLittleEndian(blockFile))
    creationTime = datetime.datetime.fromtimestamp(creationTimeTimestamp).strftime('%d.%m.%Y %H:%M')
    bits = hexToInt(readIntLittleEndian(blockFile))
    nonce = hexToInt(readIntLittleEndian(blockFile))
    countOfTransactions = readVarInt(blockFile)
    
    print("Magic Number: ", magicNumber)
    print("Blocksize: " + str(blockSize))
    print("Version: " + str(version))
    print("Previous Hash: ", previousHash)
    print("Merkle Hash: ", merkleHash)
    print("Time: " , creationTime)
    print("Bits: " + str(bits))
    print("Nonce: " + str(nonce))
    print("Count of Transactions: " + str(countOfTransactions))
    
    for transactionIndex in range(0, countOfTransactions):
        readTransaction(blockFile)


i = 0
with open('../blocks/blk00001.dat', 'rb') as file:
    while i < 3:
        print(i)
        process_block(file)
        print("")
        print("+"*100)
        print("")
        i+=1