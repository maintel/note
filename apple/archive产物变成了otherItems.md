https://www.jianshu.com/p/c3dda3489a24

- 首先查看产物是否正确

    一般这种情况下产物都是不正确的。目前遇到的问题是 Products 下除了 applications 还多了一个文件夹。

- 解决方案

    1）静态库的skip install设置为YES
    2）将子项目中Build Phases→Copy Headers中的所有头文件（如果有的话）拉到Project下，即Public和Private下不能有文件
    3）清空子项目中的 Build Settings→Deployment→Installation Directory选项的内容   （本次遇到的问题）
    4）项目中Copy Files类型的设置Destination（目的地）设置为Products Directory

