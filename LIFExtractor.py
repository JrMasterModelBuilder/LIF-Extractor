"""
    LIF Extractor - LEGO Digital Designer LIF extractor.

    Copyright (C) 2012 JrMasterModelBuilder

    You accept full responsibility for how you use this program.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


import os
import sys

def extract(path):
    
    def uint32(offset):
        if(bytesAre == "str"):
            return (ord(fileData[offset]) * 16777216) + (ord(fileData[offset+1]) * 65536) + (ord(fileData[offset+2]) * 256) + ord(fileData[offset+3])
        else:
            return (fileData[offset] * 16777216) + (fileData[offset+1] * 65536) + (fileData[offset+2] * 256) + fileData[offset+3]
    
    def uint16(offset):
        if(bytesAre == "str"):
            return (ord(fileData[offset]) * 256) + ord(fileData[offset+1])
        else:
            return (fileData[offset] * 256) + fileData[offset+1]
    
    def recurse(prefix, offset):
        if(prefix == ""):
            offset += 36
        else:
            folderList.extend([prefix])
            offset += 4
            
        for i in range(uint32(offset)):
            offset += 4
            entryType = uint16(offset)#1 = directory, 2 = file
            offset += 6
            #Build the name.
            entryName = os.sep
            #Check both integer and byte for different versions of Python.
            while(fileData[offset+1] != 0 and fileData[offset+1] != b"\x00"):
                if(bytesAre == "str"):
                    entryName += fileData[offset+1]
                else:
                    entryName += chr(fileData[offset+1])
                offset += 2
            offset += 6
            
            if(entryType == 1):
                #Recurse through the director, and update the offset.
                packedFilesOffset[0] += 20
                offset = recurse(prefix + entryName, offset)
            elif(entryType == 2):
                #File offset.
                packedFilesOffset[0] += 20
                fileOffset = packedFilesOffset[0]
                #File size.
                fileSize = uint32(offset) - 20
                offset += 24
                packedFilesOffset[0] += fileSize
                fileList.extend([[prefix + entryName, fileOffset, fileSize]])
        #Return the offset at the end of this run to update parent runnings.
        return offset
    
    print("PROCESSING: " + path)
    #Open the file if valid.
    try:
        with open(path, "rb") as f:
            fileData = f.read()
    except IOError as e:
        print("\tERROR: Failed to read file.")
        return False
    
    if(len(fileData) < 4 or fileData[0:4] != b"LIFF"):
        print("\tERROR: Not a LIF file.")
        return False
    
    print("\tEXTRACTING: Please wait.")
    
    #Recurse through, creating a list of all the files.
    packedFilesOffset = [84]#Array for non-global function-modifiable variable.
    folderList = []
    fileList = []
    #Check if this version of Python treats bytes as int or str
    bytesAre = type(b'a'[0]).__name__    
    #Recuse through the archive.
    recurse("", (uint32(72)+64))
    
    #Create output path from input path.
    if(path[-4:].lower() == ".lif"):
        outFolder = path[:-4]
    else:
        outFolder = path
    #Create the first non-existant folder to extract to.
    if os.path.exists(outFolder):
        i = 1
        while(os.path.exists(outFolder + "_" + str(i))):
            i += 1            
        outFolder = outFolder + "_" + str(i)
    
    #Make the output folder.
    os.makedirs(outFolder)
    
    #Create all the folders we need to extract to.
    for a in folderList:
        if(a[0] == ""):
            continue
        if not os.path.exists(outFolder + a):
            os.makedirs(outFolder + a)
    
    #Loop through the list of files, saving them.
    for a in fileList:
        f = open((outFolder + a[0]), "wb")
        f.write(fileData[a[1]:a[1]+a[2]])
        f.close()
    
    print("\tCOMPLETE: " + str(len(fileList)) + " files in " + str(len(folderList)) + " folders extracted.")
    return True

#Detect if executable or not.
fileName = sys.argv[0].split(os.sep).pop()
if(fileName[-3:] == ".py" or fileName[-4:] == ".pyw"):
    runCommand = "python " + fileName
else:
    runCommand = fileName

if(len(sys.argv) > 1):
    for i in range(1, len(sys.argv)):
        extract(sys.argv[i])
else:
    print("LIF Extractor 1.0\n\nThis program will extract LIF archives to an adjacent folder.\n\nCOPYRIGHT:\n\t(C) 2012 JrMasterModelBuilder\n\nLICENSE:\n\tGNU GPLv3\n\tYou accept full responsibility for how you use this program.\n\nUSEAGE:\n\t" + runCommand + " <LIST_OF_FILE_PATHS>")

