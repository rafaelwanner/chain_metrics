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