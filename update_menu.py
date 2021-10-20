#conding=utf8  
import os 

root = os.walk(r"./")  

file = open('README.md', 'w')
try:
    file.write('')
    file.write("**总目录：**\n")
    length = 0
    for path,dir_list,file_list in root:  
        # print("第一层")
        # file.write('文件夹名称:' + path)
        # 隐藏文件夹跳过
        if path.replace("./","").startswith(".") or path == './img':
            continue
        need_add_details = length != 0
        length = len(path.replace("./","").split('/'))
        # if(length ==  1):
        #     if need_add_details:
        #         file.write("</details>\n")
        #     file.write("<details>\n<summary>" + path.replace('./',"") +"</summary>\n\n")
        if length > 2:
            for i in range(length -3):
                file.write(" ")
            file.write("- ["+path.replace('./',"") +"](" +path.replace(" ","%20") + ")")
            file.write('\n')
        else:
            for i in range(length):
                file.write("#")
            file.write(" ["+path.replace('./',"") +"](" +path.replace(" ","%20") + ")")
            file.write('\n')
            file.write('\n')
        for dir_name in dir_list:
            if length == 1 and (not(dir_name.replace("./","").startswith(".") or dir_name == './img')):
                file.write("- ["+dir_name +"](#" +dir_name.replace(" ","%20") + ")\n")
        for file_name in file_list:  
            if file_name.endswith('.md'):
                if length > 2:
                    for i in range(length -1):
                        file.write(" ")
                # print("第二层")
                new_file_name = file_name
                new_file_name = new_file_name.replace(" ","")
                new_file_name = new_file_name.replace(".md","")
                file_path_str =   os.path.join(path, file_name).replace(" ","%20")
                file.write("- ["+new_file_name +"](" +file_path_str + ")")
                # file.write(os.path.join(path, file_name) )
                file.write('\n')
                # print(os.path.join(path, file_name) )
        file.write('\n')
    
    # file.write("</details>")
finally:
    file.close()      