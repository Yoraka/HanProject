# 遍历parsed_json文件夹下的所有json文件，
# 遍历每个json文件，查找有没有任何只有character的object
# 如果有，就把这个object的character写入到一个txt文件中

import os
import json

# 遍历parsed_json文件夹下的所有json文件
def traverseJsonFiles():
    jsonFiles = []
    for root, dirs, files in os.walk(".\output\parsed_json"):
        for file in files:
            if file.endswith(".json"):
                jsonFiles.append(os.path.join(root, file))
    return jsonFiles

# 遍历每个json文件，每个json文件里都有一个json数组
# json数组里有很多个json对象，查找有没有任何只有character的json对象
# 如果有，就把这个object整个加入到characterOnlyObject数组中
def findCharacterOnlyEntry(jsonFiles):
    characterOnlyObject = []
    for jsonFile in jsonFiles:
        with open(jsonFile, 'r') as f:
            data = json.load(f)
            for entry in data:
                characterOnlyObject.extend([entry for entry in data if entry["character"] and not any(entry[key] for key in entry if key != "character")])
    return characterOnlyObject

# 如果有，就把这个object的character写入到一个txt文件中
# 如果txt文件不存在，就创建一个
# 如果characterOnlyObject = []里面没有元素，就向txt文件写入"None"
def writeCharacterOnlyEntry(characterOnlyObject):
    with open('.\output\checkpoint\characterOnlyEntry.txt', 'w') as f:
        if characterOnlyObject == []:
            f.write("None")
        else:
            for entry in characterOnlyObject:
                f.write(entry['character'] + '\n')

def run():
    jsonFiles = traverseJsonFiles()
    characterOnlyJsonFiles = findCharacterOnlyEntry(jsonFiles)
    writeCharacterOnlyEntry(characterOnlyJsonFiles)
    return 1