<!-- TOC -->autoauto- [implementation() not mathod](#implementation-not-mathod)auto- [output.outputFile 报错](#outputoutputfile-报错)auto- [Could not get unknown property 'apkVariantData' for object of type](#could-not-get-unknown-property-apkvariantdata-for-object-of-type)auto- [遇到 Error:Execution failed for task ':xxxxxxx'. 的解决办法](#遇到-errorexecution-failed-for-task-xxxxxxx-的解决办法)auto- [代理问题无法下载依赖包](#代理问题无法下载依赖包)auto- [遇到一些奇葩的问题](#遇到一些奇葩的问题)auto- [Failed to notify project evaluation listener](#failed-to-notify-project-evaluation-listener)autoauto<!-- /TOC -->

# implementation() not mathod 

这个是因为 gradle 版本过低的原因，升级到3.0.0以上就好了

# output.outputFile 报错

在 gradle 3.0 以下版本是没有问题的，但是在gradle 3.0 以上就有问题了。

解决办法，在3.0以上使用 outputs.first().outputFile 来替代。

# Could not get unknown property 'apkVariantData' for object of type 

完整错误

> Error:Could not get unknown property 'apkVariantData' for object of type com.android.build.gradle.internal.api.ApplicationVariantImpl.

这个是因为在2.x中的 getApkVariantData() 函数在3.x中被修改成了 getVariantData() ，所以 ApplicationVariantImpl 类的 apkVariantData 属性就不存在了。

解决办法：降低 gradle 的版本

> 遇到问题的地方是 tinker 中，使用版本的1.7.5，升级到1.9.2版本后解决此问题

# 遇到 Error:Execution failed for task ':xxxxxxx'. 的解决办法

打包或者 build 项目的时候有时候会报这种错误，某个任务执行失败。比如：

    Error:Execution failed for task ':test:processDebugManifest'.
    > Manifest merger failed with multiple errors, see logs

但是又找不到 log 在哪，可以在 Terminal 执行如下命令来获取详细的错误信息：

    gradlew processDebugManifest --stacktrace

即出现什么任务错误，就单独执行什么任务。


# 代理问题无法下载依赖包

现象：明明已经配置了代理，并且测试 connect 成功，但是编译的时候还是不能下载依赖包。

解决：在全局的 build.gradle 中配置了一个新的仓库 mavenCentral()。

说明：mavenCentral() 和 jcenter() 是类似的，但是他们是两个完全不同的仓库，在低版本的 android stuido 中 默认的仓库是 mavenCentral(), 但是 mavenCentral() 上传比较麻烦，所以后来 google 把默认仓库换成了 jcenter()。

# 遇到一些奇葩的问题
 
 比如 有某个包总是无法下载下来，而且这个包是可以直接访问的

 这个时候可以把 android studio 安装目录下的 .gradle 文件夹删了 重新下载。


# Failed to notify project evaluation listener

使用命令行构建时遇到下面的错误：

    FAILURE: Build failed with an exception.

    * What went wrong:
    A problem occurred configuring project ':pointread'.
    > Failed to notify project evaluation listener.
    > org.gradle.api.tasks.compile.CompileOptions.setBootClasspath(Ljava/lang/String;)V

后来对比了输出日志发现问题，在环境变量中配置的 gradle 版本是 5.4.1，但是构建项目的 gradle-tools 是 2.3.2 默认需要使用的是 4.10.1，使用命令行编译的时候强制使用了 5.4.1 导致版本不一致导致编译失败。

重新配置环境变量后也需要重启一下 Android stuido 才行，否则 Android studio 自带的命令行工具不起效。


# 阿里云仓库失效问题

原有配置

```
        maven { url 'http://maven.aliyun.com/nexus/content/groups/public/' }
        maven { url 'http://maven.aliyun.com/nexus/content/repositories/jcenter' }
```

build 的时候遇到问题 `Resource missing. [HTTP GET: https://maven.aliyun.com/nexus/content/groups/public` 链接点进去看一下提示

```
当前页面不可用.

暂不支持通过仓库URL浏览仓库内容，但不影响构建使用。浏览所有可用仓库及仓库内容，请访问首页:https://maven.aliyun.com
```

经过查看发现是阿里云仓库的访问地址发生了变化修改配置如下解决问题：

```
        maven { url 'https://maven.aliyun.com/repository/public/' }
        maven { url 'https://maven.aliyun.com/repository/jcenter/' }
```