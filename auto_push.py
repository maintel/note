#conding=utf8

# 自动更新 readme 并提交
# 命令 python auto_push.py commitMsg branchName
import os
import sys
# 不传递参数

os.system("python update_menu.py")
os.system("git add .")
os.system("git commit -m %s" %sys.argv[1])
os.system("git push origin %s" %sys.argv[2])