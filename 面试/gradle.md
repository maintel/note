# gradle 的结构，作用

```bash
MyApp/                  # 项目根目录
├── build.gradle
├── setting.gradle
└── app/                # module
    ├── build.gradle
    ├── build/
    ├── libs/
    └── src/            # 源码目录
```

- settings.gradle 

  用于指示 Gradle 在构建应用时应将哪些模块包括在内
- build.gradle  

  用于定义适用于项目中所有模块的构建配置
  - buildscript

    默认情况下用来定义项目中所有模块共用的 Gradle 存储区和依赖项
- app/build.gradle

  用于配置适用于其所在模块的构建设置。

# gradle 在 Android 打包中是如何执行的

# Library 和 主工程的 gradle 的区别

build.gradle 中的内容不一样。

主工程的是：`apply plugin: 'com.android.application'`
Library中的是：`apply plugin: 'com.android.library'`