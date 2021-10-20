#conding=utf8
import os
import sys
# 不传递参数

os.system("python update_menu.py")
os.system("git add .")
os.system("git commit -m %s" %sys.argv[1])
os.system("git push origin %s" %sys.argv[2])