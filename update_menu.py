#conding=utf8  
import os 

root = os.walk(r"./")  

file = open('README.md', 'w')

try:
    file.write('')
    length = 0
    hasDetailsStart = {}
    for path,dir_list,file_list in root:  
        if path.replace("./","").startswith(".") or path == './img':
            continue
        print(path)
        length = len(path.replace("./","").split('/'))
        print(length)
        print(hasDetailsStart.get(length,False))
        if hasDetailsStart.get(length,False):
            file.write("</details>\n\n")
            hasDetailsStart.update({length:False})
        if length == 1 :
            for key, value in hasDetailsStart.items():
                if value:
                    file.write("</details>\n\n")
                    hasDetailsStart.update({key:False})
        else: 
            if hasDetailsStart.get(length,False):
                file.write("</details>\n\n")
                hasDetailsStart.update({length:False})
        if length > 2:
            for i in range(length -3):
                file.write(" ")
            file.write("- ["+path.replace('./',"") +"](" +path.replace(" ","%20") + ")")
            file.write('\n')
        else:
            # 添加一级标题
            if path != "./":
                for i in range(length):
                    file.write("#")
                file.write(" ["+path.replace('./',"") +"](" +path.replace(" ","%20") + ")")
                file.write("\n\n<details>\n<summary>" + path.replace('./',"") +"</summary>\n\n")
                hasDetailsStart.update({length:True})
                file.write('\n')
        if length == 1 and path == "./":

            for dir_name in dir_list:
                print(dir_name)
            # 添加目录
                if (not(dir_name.replace("./","").startswith(".") or dir_name == './img')):
                    file.write("- ["+dir_name +"](#" +dir_name.replace(" ","%20") + ")\n")
            
            print("==================>>>>>>>>")
        if len(dir_list) > 0:
            print("==================<<<<<<<<")
            print("还有子目录")
            print("==================<<<<<<<<")
        for file_name in file_list:
            print("开始遍历文件列表：")
            print(file_name)
            if file_name.endswith('.md') and not(file_name.startswith("README")):
                if length > 2:
                    for i in range(length -1):
                        file.write(" ")
                new_file_name = file_name
                new_file_name = new_file_name.replace(" ","")
                new_file_name = new_file_name.replace(".md","")
                file_path_str =   os.path.join(path, file_name).replace(" ","%20")
                file.write("- ["+new_file_name +"](" +file_path_str + ")")
                file.write('\n')
        file.write('\n')
        print("==================")
finally:
    file.close()      