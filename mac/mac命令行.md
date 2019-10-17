# 呼出终端

command + 空格键 输入`ter` 选择终端 回车即可

# 命令行 tab 自动补全

终端输入

> nano .inputrc

然后输入

	set completion-ignore-case on
	set show-all-if-ambiguous on
	TAB: menu-complete

按 Control + O 再按回车保存。

重启客户端。

# 终端打开 finder

如果进入到一个比较深的路径然后需要打开这个文件夹有两种方式

- 首先 pwd 然后在finder 中`前往文件夹`中粘贴；

- 更简单的方法，输入`open .` 即可打开，注意后面的`.`。

