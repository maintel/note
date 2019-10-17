# vscode 在 linux 上安装

之前一直下载 linux 的安装包安装，总是卡死在等待安装，下面索性使用压缩包进行安装。

# 从官网下载最新的文件

[下载地址](https://code.visualstudio.com/docs/?dv=linux64)

# 解压

> tar -xzvf code-stable-code_1.19.2-1515599945_amd64.tar.gz

# 移动到 /usr/local/ 目录（需要权限）

> mv VSCode-linux-x64 /usr/local/

# 然后给可执行权限

> chmod +x /usr/local/VSCode-linux-x64/code

# 复制一个图标到 icons 目录

> cp /usr/local/VSCode-linux-64/resources/app/resources/linux/code.png /usr/share/icons/

# 创建启动器

直接使用 vim 命令

> vim /usr/share/applications/VSCode.desktop

然后输入：

```
[Desktop Entry]
Name=Visual Studio Code
Comment=Multi-platform code editor for Linux
Exec=/usr/local/VSCode-linux-x64/code
Icon=/usr/share/icons/code.png
Type=Application
StartupNotify=true
Categories=TextEditor;Development;Utility;
MimeType=text/plain;
```

保存退出，然后复制到桌面

> cp /usr/share/applications/VSCode.desktop ~/桌面/

# 设置可执行程序

通过上面的步骤，在桌面就能看到一个 vscode 的启动标志，但是双击执行可能会出现未受信任的程序这些，这个时候右键--属性--权限，将可执行程序打勾就可以了。

**同样的其他的应用程序安装的时候也过程也和上面类似**