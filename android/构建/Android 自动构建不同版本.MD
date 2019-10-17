# 背景

在日常的开发中，特别是进入版本快速迭代的时候，需要不停的修改配置，测试环境、线上环境配置，测试包、正式包的打包等等，不但过程繁琐而且还容易出错，所以查询了相关资料尽量实现自动化配置。

目标：

- 根据构建环境自动配置代码参数。

- 自动打包不同的KEY的app。

- apk输出路径和名称配置。

接下来就开始吧。

# 技术概要

本文的目标主要都是通过修改 app/build.gradle 文件来实现的。

> gradle 提供了构建项目的一个框架，而它本身来使用 Groovy 来声明设置，Groovy 本身也可以理解成一个语言，有自己的语法、可执行等等。

# 根据构建环境自动配置代码参数

可能概括的不是很好，举个例子就是在项目开发过程中，测试开发环境和线上环境肯定不会使用同样的服务器，这里就是通过 gradle 来实现自动化的配置。

下面就通过这个例子来说明。

例如之前的代码：

![自动化构建old接口](http://blogqn.maintel.cn/自动化构建服务器接口old.png?e=3079754286&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:FbLV8JK8VcdWxKaoVWkgHhE3fkI=)

每次发版的时候都要修改上面的代码来切换接口环境，这样做虽然不是很麻烦，但是毕竟不够优雅，而且保不准哪次就忘了。所以引入了自动化构建。

首先在 app/bulid.gradle 中添加如下代码：

```
android {
    ...
     buildTypes {
          release {
              buildConfigField("String", "BASE_URL", "\"http://www.google.com/\"")
              buildConfigField("String", "Base_QINIU", "\"http://www.qiniu.com/\"")
          }
          debug{
              debuggable true  //表示是debug版本
              buildConfigField("String", "BASE_URL", "\"http://www.baidu.com/\"")
              buildConfigField("String", "Base_QINIU", "\"http://www.qiniu.com/\"")
          }
     }
}
```

首先 ReBuild 一下，然后修改之前接口文件代码：

```java
    String BASE_URL = BuildConfig.BASE_URL; 
    String Base_QINIU = BuildConfig.Base_QINIU; 
```

这样再直接运行的时候就会自动使用 debug 版本的接口，而正式打包的时候则会使用正式的接口。

# 自动打包不同KEY的app

同样的可以通过配置来实现一次打包不同签名文件的apk。配置方法如下：

还是在 app/build.gradle 中：

```
android {
    ...

    signingConfigs {
        release {
            keyAlias 'blelock'  //别名
            keyPassword 'xxxx'  //别名密码
            storeFile file('../lockBle.jks')  //文件路径  默认根目录为app下，所以 ../代表app目录的上级目录
            storePassword 'xxxx'  //密码
        }
        debug {
            keyAlias 'blelock_debug'
            keyPassword 'xxxx'
            storeFile file('../lockBle_debug.jks')
            storePassword 'xxxx'
        }
    }

     buildTypes {
          release {
              signingConfig signingConfigs.release  //使用 release 配置的key
          }
          debug{
              debuggable true  //表示是debug版本
              signingConfig signingConfigs.debug   //使用 debug 配置的key
          }
     }
}
```

然后点击 Android studio 中最右边的 Gradle 标签，点击 root - Tasks - build 双击执行 assemble 等待执行完以后，就能在 app/build/outputs/apk 文件夹下看到两个文件，分别为 app-debug.apk 和 app-release.apk。

![](http://blogqn.maintel.cn/执行build-assemable.png?e=3079756136&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:nQFiJGPF10NwJMFzBcUY_bUkPJE=)

![](http://blogqn.maintel.cn/自动签名apk1.png?e=3079756181&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:FataGEYtRIL2PjEKHjWpN_d10E0=)

# apk 输出路径和名称配置

通过上面实现了自动对 apk 进行不同签名的功能，但是输出 apk 包的位置和名称不够理想和直观，所以再接着进行修改,添加如下。

```
android {
    ...
     buildTypes {
          release {
            applicationVariants.all { variant ->
                variant.outputs.each { output ->
                    def outputFile = output.outputFile
                    def fileName;
                    if (outputFile != null && outputFile.name.endsWith('.apk')) {
                        if (variant.buildType.name.equals('release')) {  
                            fileName = "apk${defaultConfig.versionName}.apk"  //修改正式包的名称 为 apk+版本号.apk
                        } else if (variant.buildType.name.equals('debug')) {
                            //修改测试包的名称为 apk+版本号-test.apk
                            fileName = "AiLock${defaultConfig.versionName}-test.apk"  
                        }
                        output.outputFile = new File("./apk", fileName)  //修改输出路径为 根/apk 文件夹下，没有则会自动创建
                    }
                }
            }
          }
     }
}
```

然后同样执行上面的 assemble 以后，会在项目根目录生成一个 apk文件夹。

![](http://blogqn.maintel.cn/生成的apk.png?e=3079757689&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:RtTmEq3ha-pR5aT66b4EugAxx3Q=)

以上就是一个简单的自动化配置的过程，当然还有很多其他的配置，以后慢慢研究吧。