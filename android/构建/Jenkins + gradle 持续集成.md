本篇文章的目标是实现一个基于 Jenkins、Gradle、git的持续集成环境。

上一篇实现了 [gradle 自动化构建](http://blog.maintel.cn/blog/2017/03/gradle%E8%87%AA%E5%8A%A8%E6%9E%84%E5%BB%BA%E9%85%8D%E7%BD%AE-%E4%B8%80.html)的功能，但是总是觉得不够智能，有没有一种办法可以使程序自动打包完成并通知相关人员呢？答案就是本篇要讲的 Jenkins。

# 持续集成

**持续集成（Continuous Integration）**

首先是持续集成，我知道持续集成还是从做后台的哥们儿那里，概念就如字面意思：

> 持续集成指的是，频繁地（一天多次）将代码集成到主干。持续集成的目的，就是让产品可以快速迭代，同时还能保持高质量。它的核心措施是，代码集成到主干之前，必须通过自动化测试。只要有一个测试用例失败，就不能集成。

与持续集成相关的，还有两个概念，分别是持续交付和持续部署。

**持续交付（Continuous delivery）**

> 频繁地将软件的新版本，交付给质量团队或者用户，以供评审。如果评审通过，代码就进入生产阶段。持续交付可以看作持续集成的下一步。它强调的是，不管怎么更新，软件是随时随地可以交付的。

**持续部署（continuous deployment）**

> 持续交付的下一步，指的是代码通过评审以后，自动部署到生产环境。

简单看概念来说本篇文章实现的功能是持续集成和持续交付，即代码持续集成后自动打包生产出测试包然后通知测试人员测试，而不用开发人员再手动的去打包发送等。

# Jenkins

[Jenkins](https://jenkins.io/) 是一个开源的持续集成工具，可以用它来实现持续集成，同样功能的软件还有 
- [Travis](https://travis-ci.com/)
- [Codeship](https://www.codeship.io/)
- [Strider](http://stridercd.com/)

下面就来实践一个持续集成的工程。

# 安装 Jenkins

首先在[这里](https://jenkins.io/download/)下载 Jenkins，Jenkins 官方提供了 war 包以及其他的个各种操作系统的安装程序。windows 平台下可以有两个选择：

- war 包

    只需运行 java -jar jenkins.war 即可

- msi 文件

    直接运行即可

本篇文章选用安装文件的方式，安装成功后会自动访问 `http://localhost:8080` ,并自动生成一个随机的密码在 `root\jenkins\secrets\initialAdminPassword`。如果启动不能成功，可能端口号冲突修改一个端口号即可。

修改端口号方法:打开 `root\jenkins.xml`找到`--httpPort=8080`修改，然后执行`net stop jenkins`和`net start jenkins`重启 Jenkins（如果提示拒绝访问，使用管理员权限）。

重新访问修改后的地址，然后填入密码等待刷新完成。

然后选择安装插件，我是直接选择左边使用推荐来自动完成，也可以选择右边自定义其中几个重要的插件 Gradle(gradle plugin)、git(git plugin)、邮件(email extension plugin)等。

等待插件下载完成要创建一个用户，创建完成即进入首页。

![](http://blogqn.maintel.cn/TIM截图20170829114554.png?e=3080777649&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:ggLh6k9SXOxaJd0jgv7VPWrkYbs=)

# 配置

- 权限配置

系统管理 - Configure Global Security，通过安全矩阵对不同角色或者组进行权限配置，具体说明请自行google。

![](http://blogqn.maintel.cn/TIM截图20170829145712.png?e=3080789153&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:g05yRNWoxALajGkXxisnZTUD_1c=)

- gradle插件配置

 gradle 插件等进行配置,这里主要是为了防止项目配置中的 gradle 和 android 项目的 gradle 版本不同导致构建失败。

系统管理 - Global Tool Configuration

![](http://blogqn.maintel.cn/TIM截图20170829115151.png?e=3080778048&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:rIqHSNf27OwDUSjydZuTWGR-ekk=)


选择 gradle配置,配置常用的 gradle 版本。可以手动指定目录，也可以选择自动安装。

![](http://blogqn.maintel.cn/TIM截图20170829115828.png?e=3080778403&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:PFPIh4V-L4tEXNq1XZhvtUKkvrE=)

- 邮件服务器配置

系统管理 - 系统设置。

这里要注意 SMTP认证 的邮箱一定要和上面 Jenkins Location 设置中系统管理员邮件地址一样，不然不能成功。配置完成可以使用测试邮件提示 `Email was successfully sent` 则代表成功。

![](http://blogqn.maintel.cn/TIM截图20170829143712.png?e=3080787927&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:J-8IRzHuAhyABZ5nI8zC1bwXhJQ=)


# 创建项目

这里假设已经有一个android gradle项目名为 JenkinsTest，并已经推送到 git 远程仓库。

- 点击创建一个新任务

![](http://blogqn.maintel.cn/TIM截图20170829114902.png?e=3080777839&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:XAe_RUlK7xKDDkgHs64OkG8KlJ8=)

这里选择`构建一个自由风格的软件项目`。选择 ok 配置项目

- 源码管理选择 git 填入 git 项目地址

![](http://blogqn.maintel.cn/TIM截图20170829141008.png?e=3080786413&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:lZYyiqufEgNYNbpRV7r84Z2ajXY=)

这里可以全局配置好直接选择账号，也可以设置 git 账号，点击`add`，

![](http://blogqn.maintel.cn/TIM截图20170829141036.png?e=3080786589&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:NHzIV4cikgmtVy6yHRa5e6BZba4=)

- 配置构建触发器

这里选择使用 `Poll SCM` (定时检查源码变更)，Jenkins 会根据配置定期的检查更新，如果有更新就下载并进行构建。他的语法如下：

总共有五个参数 * * * * *,

第一个参数代表的是分钟 minute，取值 0~59；

第二个参数代表的是小时 hour，取值 0~23；

第三个参数代表的是天 day，取值 1~31；

第四个参数代表的是月 month，取值 1~12；

最后一个参数代表的是星期 week，取值 0~7，0 和 7 都是表示星期天。

H/5 * * * * 就代表每五分钟检查一次。

![](http://blogqn.maintel.cn/TIM截图20170829141741.png?e=3080786790&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:Ym2PmBqmpTyYqIo2cX_K_favKGM=)

- 构建工具

增加构建步骤 - `Invoke Gradle script`，然后选择 Gradle 的版本，在 Tasks 中增加构建的命令

![](http://blogqn.maintel.cn/TIM截图20170829142837.png?e=3080787407&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:THm64jdST0OAq6GJ4exdze8ByqA=)

- 构建后操作

将生成的 apk 输出保存出来，如果没有在 gradle 中配置 apk 的输出路径，则默认为 `app/build/outputs/apk/*.apk`，还可以选择发送邮件通知相关人员比如测试。

![](http://blogqn.maintel.cn/TIM截图20170829144316.png?e=3080788431&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:e5UyTjmxA0ZSd6Xy-O166O7WuO0=)

至此，所有配置已经完成。

# 构建项目

配置完成以后项目目录

![](http://blogqn.maintel.cn/TIM截图20170829144819.png?e=3080788652&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:1Ubl2Omde1sN92JYyAkTRpp1S5I=)

可以点击工作空间查看获取的代码是否正确。

可以在构建历史列表看到一些以往的构建结果，点击进入可以看到一些构建结果，包含git的信息等。

![](http://blogqn.maintel.cn/TIM截图20170829145441.png?e=3080788978&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:Qx7XkhfBNCZQYkhQ1Pgn_-GED9U=)

在 Console Output 中可以看到控制台的编译输出，如果编译失败可以在这里找到一些有用的信息

![](http://blogqn.maintel.cn/TIM截图20170829145153.png?e=3080788978&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:2g8DWpNwJbOrXYbasJCQolqDpe0=)





