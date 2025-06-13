import os
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
from Crypto.Cipher import ChaCha20_Poly1305
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2

AudioVideoExtensions = {
    '.mp3', '.wav', '.aac', '.flac', '.ogg',
    '.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv'
}

FixedSaltValue = b'my_fixed_salt_1234'  # 16-byte fixed salt for PBKDF2 derivation

def deriveEncryptionKey(passwordEncodedBytes, saltValue=FixedSaltValue, iterationCount=100000, keyLength=32):
    derivedKey = PBKDF2(passwordEncodedBytes, saltValue, dkLen=keyLength, count=iterationCount, hmac_hash_module=SHA256)
    return derivedKey

def computeFileHash(fileFullPath):
    """
    计算文件SHA256哈希，返回hex字符串
    """
    hasher = hashlib.sha256()
    try:
        with open(fileFullPath, 'rb') as fileHandle:
            while True:
                chunk = fileHandle.read(8192)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as exceptionInstance:
        print(f"Error hashing file {fileFullPath}: {exceptionInstance}")
        return None

def getUniqueFilesByHash(directoryRootPath, operationMode):
    """
    遍历目录，找出待处理文件，计算哈希分组，
    返回去重后仅保留每个哈希第一个文件的列表
    """
    fileHashDict = dict()
    for currentDirectoryPath, _, fileNameList in os.walk(directoryRootPath):
        for fileName in fileNameList:
            fileExtension = os.path.splitext(fileName)[1].lower()
            fullFilePath = os.path.join(currentDirectoryPath, fileName)

            if operationMode == 'encrypt':
                if fileExtension not in AudioVideoExtensions:
                    continue
                fileHash = computeFileHash(fullFilePath)
                if fileHash is None:
                    continue
                if fileHash not in fileHashDict:
                    fileHashDict[fileHash] = [fullFilePath]
                else:
                    fileHashDict[fileHash].append(fullFilePath)

            elif operationMode == 'decrypt':
                try:
                    with open(fullFilePath, 'r', encoding='utf-8') as jsonReadFile:
                        jsonData = json.load(jsonReadFile)
                    if all(requiredKey in jsonData for requiredKey in ('nonce', 'tag', 'ciphertext')):
                        fileHash = computeFileHash(fullFilePath)
                        if fileHash is None:
                            continue
                        if fileHash not in fileHashDict:
                            fileHashDict[fileHash] = [fullFilePath]
                        else:
                            fileHashDict[fileHash].append(fullFilePath)
                except Exception:
                    continue
    # 返回去重，只保留每个哈希的第一个文件
    uniqueFileList = [fileList[0] for fileList in fileHashDict.values()]
    # 可选打印重复文件信息
    for fileList in fileHashDict.values():
        if len(fileList) > 1:
            print(f"Detected duplicate files, keeping only one: {fileList[0]}")
            for duplicateFilePath in fileList[1:]:
                print(f"   Skipped duplicate file: {duplicateFilePath}")
    return uniqueFileList

def encryptFileWithChaCha20Poly1305(fileFullPath, derivedKey):
    try:
        print(f"Encrypting file: {fileFullPath}")
        with open(fileFullPath, 'rb') as fileHandle:
            plainBytes = fileHandle.read()

        nonceBytes = get_random_bytes(12)
        cipherInstance = ChaCha20_Poly1305.new(key=derivedKey, nonce=nonceBytes)
        cipherBytes, authenticationTag = cipherInstance.encrypt_and_digest(plainBytes)

        jsonOutput = {
            'nonce': nonceBytes.hex(),
            'tag': authenticationTag.hex(),
            'ciphertext': cipherBytes.hex()
        }

        fileStatistics = os.stat(fileFullPath)

        with open(fileFullPath, 'w', encoding='utf-8') as writeFile:
            json.dump(jsonOutput, writeFile)

        os.utime(fileFullPath, (fileStatistics.st_atime, fileStatistics.st_mtime))
        return True

    except Exception as exceptionInstance:
        print(f"Error encrypting file {fileFullPath}: {exceptionInstance}")
        return False

def decryptFileWithChaCha20Poly1305(fileFullPath, derivedKey):
    try:
        print(f"Decrypting file: {fileFullPath}")
        with open(fileFullPath, 'r', encoding='utf-8') as readFile:
            jsonInput = json.load(readFile)

        nonceBytes = bytes.fromhex(jsonInput['nonce'])
        authenticationTag = bytes.fromhex(jsonInput['tag'])
        cipherBytes = bytes.fromhex(jsonInput['ciphertext'])

        cipherInstance = ChaCha20_Poly1305.new(key=derivedKey, nonce=nonceBytes)
        plainBytes = cipherInstance.decrypt_and_verify(cipherBytes, authenticationTag)

        fileStatistics = os.stat(fileFullPath)

        with open(fileFullPath, 'wb') as writeFile:
            writeFile.write(plainBytes)

        os.utime(fileFullPath, (fileStatistics.st_atime, fileStatistics.st_mtime))
        return True

    except Exception as exceptionInstance:
        print(f"Error decrypting file {fileFullPath}: {exceptionInstance}")
        return False

def processFilesWithMultithreading(derivedKey, operationMode, filesToProcessList, maximumWorkerCount=8):
    taskList = []
    with ThreadPoolExecutor(max_workers=maximumWorkerCount) as threadPool:
        for filePath in filesToProcessList:
            if operationMode == 'encrypt':
                taskList.append(threadPool.submit(encryptFileWithChaCha20Poly1305, filePath, derivedKey))
            elif operationMode == 'decrypt':
                taskList.append(threadPool.submit(decryptFileWithChaCha20Poly1305, filePath, derivedKey))
        for completedFuture in as_completed(taskList):
            completedFuture.result()

def main():
    print("Batch Audio and Video File Encryption/Decryption Tool (ChaCha20-Poly1305, Multithreading, PBKDF2 with 100000 iterations, overwrite original file keeping timestamps)")
    directoryRootPath = input("Please enter the root directory path: ").strip()
    if not os.path.isdir(directoryRootPath):
        print("The input path is not a valid directory, exiting program.")
        return

    operationMode = ''
    while operationMode not in {'encrypt', 'decrypt'}:
        operationMode = input("Please choose the operation mode (encrypt / decrypt): ").strip().lower()

    passwordInputString = input("Please enter the password: ")
    passwordEncodedBytes = passwordInputString.encode('utf-8')
    derivedKey = deriveEncryptionKey(passwordEncodedBytes)

    uniqueFiles = getUniqueFilesByHash(directoryRootPath, operationMode)
    print(f"Total unique files to process: {len(uniqueFiles)}")

    processFilesWithMultithreading(derivedKey, operationMode, uniqueFiles)

    print(f"{operationMode.capitalize()} operation completed!")

if __name__ == '__main__':
    main()
