#conding=utf8

# 自动更新 readme 并提交
# 命令 python auto_push.py commitMsg branchName
import os
import sys
# 不传递参数



if __name__ == "__main__":

    push = "auto"

    if len(sys.argv) >= 2: 
        if sys.argv[1] != "":
            push = sys.argv[1]

    os.system("python3 update_menu.py")
    os.system("git add .")
    os.system("git commit -m %s" %push)
    if sys.argv.__len__ == 2:
        os.system("git push origin %s" %sys.argv[2])
    else:
        os.system("git push origin master")
