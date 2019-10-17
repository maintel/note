# 常用命令

|命令|操作|参考|
|:---:|---:|:---|
|mkdir|创建新目录|[参考](http://www.runoob.com/linux/linux-file-content-manage.html)|
|mv|移动文件与目录，或修改名称|[参考](http://www.runoob.com/linux/linux-file-content-manage.html)|
|chmod|修改权限|[参考](http://www.runoob.com/linux/linux-file-attr-permission.html)|

# Xshell 传输文件

使用 rz、sz命令

安装 

> yum install lrzsz -y

rz 接收文件，即从win 上传文件到 linux

sz 发送文件，从 linux 发送文件到 win

# 重启和关机

关机命令

> shutdown -h now 
> halt
> poweroff

重启命令

> shutdown -r now
> reboot

# 切换到root后 java 环境变量无效

执行
> source /etc/profile

但是这样在关闭终端后再次进入又变得无效

第二种方法是，切换到 root 用户的时候 执行
> su -

su - 的意思是完全切换用户，可以获取到环境变量，su 来切换用户只能切换了用户的存取全险，但没有获取不到环境变量


# 脚本

- 创建脚本

    touch xxx.sh

- 写入文件

    echo "xxxx" > test.txt

