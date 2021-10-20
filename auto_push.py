import os
import sys
# 不传递参数
os.system("ls")    # 显示文件夹文件，不包含隐藏文件
# os.system("ls -a") # 显示文件夹所有文件，包含隐藏文件
# os.system("pwd")   # 获取当前目录
# os.system("top")   # 显示进程情况，退出需要输入 'q'.
os.system("python update_menu.py")
os.system("git add .")
os.system("git commit -m %s" %sys.argv[1])
os.system("git push origin %s" %sys.argv[2])