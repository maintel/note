#conding=utf8  
import os 

root = os.walk(r"./")  

file = open('README.md', 'w')

try:
    file.write('')
    file.write('好记性如烂笔头\n')
    length = 0
    hasDetailsStart = []
    detailStart = 0
    for path,dir_list,file_list in root:  

        if path == "./":
            file.write("\n")
            # 写目录
            for dir_name in dir_list:
                print(dir_name)
                if dir_name.startswith(".") :
                    continue
                dir_name = dir_name.replace(" ","_")
                file.write("- [" + dir_name +"](#" + dir_name + ")\n")
            file.write("\n")
            file.write("\n")
            continue

        if path.replace("./","").startswith(".") or path == './img':
            continue
        print(path)
        length = len(path.replace("./","").split('/'))
        print(length)
        dir_name = path.replace("./","").replace(" ","_")
        path = path.replace(" ","%20")
        if length == 1:
            for i in range(detailStart):
                spaces = " " * (detailStart - i - 1) * 4
                file.write(spaces + "</details>\n\n")
            detailStart = 0
            file.write("## [" + dir_name + "]("+ path + ")\n")
            file.write("\n<details>\n<summary>" + dir_name +"</summary>\n\n")
            detailStart = detailStart + 1
            print(file_list)
            for file_name in file_list:
                file.write("- [" + file_name + "]("+ path + "/" + file_name.replace(" ","%20") + ")\n")
        elif length == 2:
            if detailStart >= 2:
                detailStart = detailStart - 1
                file.write("    </details>\n\n")               
            file.write("- [" + dir_name + "]("+ path + ")\n")
            file.write("\n    <details>\n    <summary>" + dir_name +"</summary>\n\n")
            detailStart = detailStart + 1
            print(file_list)
            for file_name in file_list:
                file.write("    - [" + file_name + "]("+ path + "/" + file_name.replace(" ","%20") + ")\n")
        else:
            for file_name in file_list:
                file.write("    - [" + file_name + "]("+ path + "/" + file_name.replace(" ","%20") + ")\n")
            print(file_list)
        
        print("==================")

    for i in range(detailStart):
        spaces = " " * (detailStart - i - 1) * 4
        file.write(spaces + "</details>\n\n")   
finally:
    file.close()      