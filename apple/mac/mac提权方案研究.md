mac 开发过程中有一些操作是需要 root 权限的。调研了一下提权方案大概有以下几种：

- AppleScript

    官方提供的一个脚本语言，使用起来很简单。 `do shell script "..." with administrator privileges`

- SMJobBless

    官方提供的提权方案

- AuthorizationExecuteWithPrivileges

    这个库在 10.7 以后就已经过时了，在 10.12 上已关闭，所以不必考虑


以上三种方式 A

ppleScript 使用起来最方便，把所需的操作通过脚本的方式来实现。但是缺点是每次执行需要高权限操作的时候都需要用户输入密码，如果需要频繁获取权限的话就比较麻烦了。

SMJobBless 使用起来较为复杂，但是它可以把执行文件安装在 /Library 下，只有第一次安装的时候会需要用户输入密码，后续操作不需要再输入密码，体验最为友好。

https://blog.csdn.net/MA540213/article/details/79463899

https://fix.moe/post/macos-app-authorization

https://www.jianshu.com/p/47cfd835b35d