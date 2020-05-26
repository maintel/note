大部分问题可以参看这个文章  https://www.jianshu.com/p/b0800f590e6e


## android-apt 报错

    Error:android-apt plugin is incompatible with the Android Gradle plugin.  
    Please use 'annotationProcessor' configuration instead.

注释掉 `apply plugin: 'android-apt'`，将依赖中 `apt xxxx` 改为 `annotationProcessor xxx`