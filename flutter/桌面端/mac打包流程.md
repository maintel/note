mac 打包流程比较复杂，如果不上架 app store 的话还需要对打包的内容进行公证，公证以后才能发布给其他人员使用，否则会提示恶意软件。本篇只记录使用 Developer ID 签名公证并分发的过程，只记录大致的步骤，具体步骤的操作可以参看引用的内容。大概的打包流程可以分为以下几步：
- 配置证书
- 编译flutter
- xcode archive
- 公证
- 生成dmg文件

# 配置证书

和一般的 iOS 开发配置证书的步骤差不多，最关键的地方是需要配置 Developer ID Application 证书，更为详细的步骤可以参考 [这里](https://www.jianshu.com/p/c9c71f2f6eac)

同样的给对应的 Developer ID Application 生成 Developer ID 描述文件。将证书及描述文件下载下来安装好。

Developer ID Application 主要就是为了之后的签名公证。

# 编译 flutter

当证书都配置好以后就可以开始编译了，首先编译 flutter，使用命令

    flutter build macos --release  --build-name x.x.x --build-number xx

使用 --build-name 和 --build-number 能够灵活的指定版本号，但是要注意此时 Runner/info.plist 中的 CFBundleVersion 和 CFBundleShortVersionString 配置。

# xcode archive

等待 flutter 编译成功以后就可以使用 xcode 打包了，这里没什么好说的 菜单 product-Archive 然后等待完成就好了。

# 公证

archive 成功以后就出现 Organizer 界面，接着就可以开始上传并公证了，

- 选择  distritube app，然后选择 developer id 下一步
- 选择 upload
- 选择 对应的 team
- 选择 自定义签名
- 选择对应 develop id 的 Distribution 证书 和 描述文件，
- 等待 压缩完成，上传即可。
- 上传完成以后在 status 状态会变成等待状态，过一会儿会返回公证的结果
- 公证完成以后可以选择导出包 xxx.app

到这一步实际上已经完成了，xxx.app 就是一个可以运行的文件了，但是如果我们要发给别人安装的话最好生成一个 dmg 文件。

# 生成 dmg

使用命令行生成 dmg 文件

    hdiutil create -volname "xxxx" -srcfolder "srcfolder" -ov -format UDZO "xxxx.dmg"

解释一下上面的参数

- volname dmg 文件打开后显示的标题
- srcfolder 待打包的文件
- xxxx.dmg 生成的文件名

至此一个完整的打包流程就结束了。

# 个人的一些理解

xcode archive 过程中实际上对代码进行了一次签名，即使用在 runner- targets- signing&capabilities 中配置的签名证书和描述文件，但是公证前还需要再此使用 Developer ID Application 来进行一次签名，这两次的签名文件是可以不一致的，但第二次一定要是 Developer ID Application。

所谓打包实际上就是把 app 文件放到一个类似于压缩包一样的东西，dmg是一个特殊的格式，里面可以包含一些其他的内容，实际上在上传公证的过程中 xcode 是吧 app 压缩成 zip 上传到公证服务器进行公证。实际上我们把app压缩成一个压缩包发给其他人然后直接解压缩运行也是一样可用的。dmg 相当于在mac上更为人性化的一个操作而已。

# 遇到的问题

- Developer ID Application 安装以后无效果或者显示没有对应的签名文件

    如果确认整出安装没有问题的话，可以大退一下xcode，或者重启一下电脑。

- dmg 文件中没有拖入到 application 的选项

    给系统的“应用程序”制作一个替身，然后和 app 放同级然后一块打包即可。同时还有一些其他的操作，比如美化dmg 等等。

- codesign 想要访问钥匙串中的密码

    修改钥匙串中的访问权限，具体可以参看[这里](https://blog.csdn.net/nithumahel/article/details/79870505)

# 需要优化的地方

上述的打包流程太复杂了，实际上可以使用脚本来一键打包。[参考](./脚本一键打包.md)

# 参考资料

- [macOS开发 证书等配置/打包后导出及上架](https://www.jianshu.com/p/c9c71f2f6eac)
- [为 app 签名以通过“门禁”验证](https://developer.apple.com/cn/developer-id/)
- [macOS 开发 - 打包生成 dmg (步骤详解配图)](https://blog.csdn.net/lovechris00/article/details/78029337)
- [codesign 想要访问您的钥匙串中的密钥](https://blog.csdn.net/nithumahel/article/details/79870505)
- [Mac开发-公证流程记录Notarization-附带脚本](https://blog.csdn.net/shengpeng3344/article/details/103369804)