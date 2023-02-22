# -*- coding: utf-8 -*-
"""
Created on Sun Jan  9 08:19:22 2022

@author: Ryed
"""

import random

alphabet = []
rotSixteen = []


def normalize():
    for x in "QRSTUVWXYZABCDEFGHIJKLMNOP5678901234={[}]|\:;\"\'<,>.?/~`!@#$%^&*()-_+".lower():
        rotSixteen.append(x)
    rotSixteen.append("--")
    for y in "abcdefghijklmnopqrstuvwxyz0123456789~`!@#$%^&*()-_+={[}]|\:;\"\'<,>.?/ ":
        alphabet.append(y)
normalize()


def decrypt(encryptionCode):
    encryptionCode = encryptionCode[alphabet.index(encryptionCode[0])+1:]
    layerOne = []
    finalizeBinary = []
    decryptedValue = []
    value = []
    count = 0
    countTwo = 0
    lowerBound = alphabet.index(encryptionCode[len(encryptionCode)-2]) 
    upperBound = alphabet.index(encryptionCode[len(encryptionCode)-1])+1 
    midBound = alphabet[lowerBound:upperBound]
    for match in encryptionCode[0:len(encryptionCode)-2].lower():
        count = count +1
        check = False
        for v in midBound:
            if match == v:
                layerOne.append('1')
                check = True
                break
        if check == False:
            layerOne.append('0')
    finalizeBinary = [''.join(layerOne[0:])]
    for loop in finalizeBinary:
        binToConvert  = loop
    convertedBin = ''.join(chr(int(binToConvert[p*8:p*8+8],2)) for p in range(len(binToConvert)//8))
    for fin in convertedBin:
        countTwo = countTwo+1
        if fin == "-" and convertedBin[countTwo] == "-":
            value.append(alphabet.index(" "))
        elif fin == "-" and convertedBin[countTwo-2] == "-":
            value.append("")
        else:
            value.append(rotSixteen.index(fin))
    for done in value:
        if done == "":
            decryptedValue.append("")
        else:
            decryptedValue.append(alphabet[done])
    decryptionMain = ''.join(decryptedValue[0:])
    return decryptionMain


