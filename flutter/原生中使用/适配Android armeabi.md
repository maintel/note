由于 flutter 在设计之初就不支持 armeabi 架构的 cpu，若以如果原生工程无法修改的情况下就要介入 flutter 的编译过程来适配 armeabi。

不同版本的 flutter 适配方案也不太一样。

# 1.9 版本以下

## 1.5.4 以下

编写脚本将本地的 flutter engine 复制一份 armeabi-v7a 的到 armeabi 下。

    cd $FLUTTER_ROOT/bin/cache/artifacts/engine
    for arch in android-arm android-arm-profile android-arm-release; do
        pushd $arch
        cp flutter.jar flutter-armeabi-v7a.jar # 备份
        unzip flutter.jar lib/armeabi-v7a/libflutter.so
        mv lib/armeabi-v7a lib/armeabi
        zip -d flutter.jar lib/armeabi-v7a/libflutter.so
        zip flutter.jar lib/armeabi/libflutter.so
        popd
    done

如果是 window 环境则可以使用以下脚本（解压缩使用的 bandizip 也可以替换成其他解压软件）

    for %%I in (android-arm,android-arm-profile,android-arm-release) do (
        copy .\%%I\flutter.jar .\%%I\flutter_bak.jar
        call Bandizip.exe x %%I/flutter.jar 
        move %%I/lib/armeabi-v7a %%I/lib/armeabi
        call bc c %%I/flutter.jar %%I/io %%I/lib
        del /s /q %%I\io
        rd /s /q %%I\io
        del /s /q %%I\lib
        rd /s /q %%I\lib
    )
    pause

或者也可以手动一个一个文件夹处理。

# 1.9.1

在1.9.1 版本 flutter 编译的产物和之前不太一样，多出来了一个 libapp.so，所以除了上一步我们还要再处理以下这个 libapp.so，

然后在 flutterRoot\packages\flutter_tools\gradle\flutter.gradle中将

    private static final String ARCH_ARM32 = "armeabi-v7a";

    改为

    private static final String ARCH_ARM32 = "armeabi";

或者这一步新加一个标记位

    private static final String PLATFORM_ARM32_V7A  = "android-arm-v7a";
    private static final String ARCH_ARM      = "armeabi";

    在 PLATFORM_ARCH_MAP 中添加

    (PLATFORM_ARM32_V7A)    : ARCH_ARM32,

    在 ABI_VERSION 中添加

    (ARCH_ARM)        : 1

第二种方法的好处是在编译的时候可以同时编译出 armeabi-v7a 和 armeabi 的包。执行命令 `flutter build aar --target-platform android-arm,android-arm-v7a`

# 1.12 以上版本

1.12 以上版本 flutter 引擎有了新的变化，编译产物和之前版本又有了区别 ，1.12 版本中Flutter将engine产物已经从Flutter module aar产物中剥离，改为用远程Maven仓形式提供给Native端。

所以上面的针对 1.5 版本的修改方式已经不太适用需要新的适配方案，但是核心思想还是不变的，就是获取到 armeabi 版本的 flutter 引擎。

首先还是像 1.9.1 一样修改 flutterRoot\packages\flutter_tools\gradle\flutter.gradle 中的编译参数，不过除了上面的修改还要再修改一些其他内容：

将
          from("${compileTask.intermediateDir}/${abi}") {
                    include "*.so"
                     // Move `app.so` to `lib/<abi>/libapp.so`
                    rename { String filename ->
                          return "lib/${abi}/lib${filename}"
                       }
           }

修改为

         if(abi == "armeabi"){
            // 在这里将编译产物的 armeabi-v7a 拷贝到 armeabi 中
            from("${compileTask.intermediateDir}/armeabi-v7a"){
                include "*.so"
                rename { String filename ->
                        return "lib/armeabi/lib${filename}"
                        }
                }
        }else{
            from("${compileTask.intermediateDir}/${abi}") {
                include "*.so"
                // Move `app.so` to `lib/<abi>/libapp.so`
                rename { String filename ->
                        return "lib/${abi}/lib${filename}"
                        }
            }
        }

接下来是获取到 flutter 引擎，本身思路还是将现有的 flutter 引擎的 v7a 版本拿来用但是编译成功后打开黑屏，看来如果想要成功打出 armeabi 的包需要修改 flutter 引擎才行。

不过已经有人针对 1.12 版本做了适配（感谢 58同城 的技术）项目地址 https://github.com/wuba/magpie_sdk。

将他们的armeabi 相关的 flutter 引擎包下载下来以后上传到自己的 maven 仓库，然后再在 flutter.gradle 的 addFlutterDependencies 方法中 repositories 中添加仓库地址就能正常打包了，正常使用了，

    project.rootProject.allprojects {

        repositories {
            maven {
                url "xxxxx"
            }
        }
    }


在上传 maven 仓库的时候需要注意的就是  flutter 引擎的版本包问题，flutter 引擎的版本可以在 flutterRoot\bin\internal\engine.version 中查看。
