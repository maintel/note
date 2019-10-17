
# 博客

[Gradle 完整指南（Android)](http://www.jianshu.com/p/9df3c3b6067a)

# 编辑 gradle 时很卡的解决办法

- 断网

- 安装 Google Repository 和 Android Support Repository

# 加快构建速度

- 开启并行编译

    org.gradle.parallel=true

- 加大可用内存

    org.gradle.jvmargs=-Xmx4608M

如果可用内存太少可以在 Gradle Console 中看到一些提示：

    To run dex in process, the Gradle daemon needs a larger heap.
    It currently has 1024 MB.
    For faster builds, increase the maximum heap size for the Gradle daemon to at least 4608 MB (based on the dexOptions.javaMaxHeapSize = 4g).
    To do this set org.gradle.jvmargs=-Xmx4608M in the project gradle.properties.

- 开启编译守护进程

    org.gradle.daemon=true

# 读取配置文件

一个名称为 local.properties 的配置文件，内容如下：

```Properties
    sdk.dir=/Users/Yang/Library/Android/sdk
    keystore.location=/Users/Yang/Desktop/other/doc/keystore.jks
```
读取上面的配置文件：

```Groovy
            Properties properties = new Properties()  //新建一个配置文件类
            //读取配置文件
            properties.load(project.rootProject.file('local.properties').newDataInputStream()) 
            //读取到其中的一些内容 
            def sdkDir = properties.getProperty('keystore.location')
```


# android studio 向手机安装 apk 时的命令输出

$ adb install-multiple -r /Users/Yang/Desktop/Android/TinkerDemo/app/build/intermediates/split-apk/debug/dep/dependencies.apk /Users/Yang/Desktop/Android/TinkerDemo/app/build/intermediates/split-apk/debug/slices/slice_3.apk /Users/Yang/Desktop/Android/TinkerDemo/app/build/intermediates/split-apk/debug/slices/slice_0.apk /Users/Yang/Desktop/Android/TinkerDemo/app/build/intermediates/split-apk/debug/slices/slice_2.apk /Users/Yang/Desktop/Android/TinkerDemo/app/build/intermediates/split-apk/debug/slices/slice_1.apk /Users/Yang/Desktop/Android/TinkerDemo/app/build/intermediates/split-apk/debug/slices/slice_5.apk /Users/Yang/Desktop/Android/TinkerDemo/app/build/intermediates/split-apk/debug/slices/slice_7.apk /Users/Yang/Desktop/Android/TinkerDemo/app/build/intermediates/split-apk/debug/slices/slice_4.apk /Users/Yang/Desktop/Android/TinkerDemo/app/build/intermediates/split-apk/debug/slices/slice_6.apk /Users/Yang/Desktop/Android/TinkerDemo/app/build/intermediates/split-apk/debug/slices/slice_8.apk /Users/Yang/Desktop/Android/TinkerDemo/app/build/intermediates/split-apk/debug/slices/slice_9.apk /Users/Yang/Desktop/Android/TinkerDemo/app/build/outputs/apk/app-debug.apk 
Split APKs installed
$ adb shell am startservice com.demo.tinkerdemo/com.android.tools.fd.runtime.InstantRunService
$ adb shell am start -n "com.demo.tinkerdemo/com.demo.tinkerdemo.MainActivity" -a android.intent.action.MAIN -c android.intent.category.LAUNCHER
Connected to process 30679 on device vivo-vivo_y51a-4baba797

