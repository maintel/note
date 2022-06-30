针对mac平台编译后的可执行文件在接入到mac工程并打包上传公证出现 `The executable does not have the hardened runtime enabled.`。

**解决方案：**

对golang 编译出的可执行文件进行签名并开启 hardened runtime ，具体方法如下：

    codesign -f --deep --options runtime --sign 'Developer ID Application: xxxxxx' filename

然后可以使用  `codesign -dv filename` 验证，正确签名应该有以下输出：

    Identifier=pac
    Format=Mach-O thin (x86_64)
    CodeDirectory v=20500 size=303 flags=0x10000(runtime) hashes=4+2 location=embedded
    Signature size=9017
    Timestamp=Jun 30, 2022 at 6:14:07 PM
    Info.plist=not bound
    TeamIdentifier=xxxxx
    Runtime Version=10.12.0
    Sealed Resources=none
    Internal requirements count=1 size=164

flags=0x10000(runtime) 表示开启成功。