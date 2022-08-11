这里记录一下 windows 自动化打包的一些经验。

由于在windows上执行 shell 脚本不太方便， bat 脚本又不太会写也不想花时间再研究，所以在windows上就用 python 来实现自动化打包。


# 打包

windows 打包实际上和其他应用打包一样直接调用 flutter build 命令即可。

    os.system(f"flutter build windows --release --dart-define=VERSION_NAME={verName}  --dart-define=VERSION_CODE={verCode}")

其中 VERSION_NAME 和 VERSION_CODE 用来指定版本号了，因为 windows 的 build-tools 中默认不处理 buildNum 等参数， 所以这里使用了自定义的版本号参数。

当打包完成以后生成的文件就在 /build/windows/runner/Release 下，此时理论上来说我们所需的文件都已经有了，可以直接点开 exe 使用了。但是生产环境中存在以下问题：

- 往往需要我们把应用程序发给客户，直接发送一个文件夹给别人肯定是不行的，因此我们需要把 release 下的文件打包成一个安装包发给客户；
- 很多时候我们使用的一些第三方库或者处理一些兼容性问题的时候需要手动拷贝一些 dll 或者其他可执行文件放到我们应用中以保证程序能正常运行。

下面就来分别解决这两个问题。

# 打包成安装包

这一步我们可以使用 Visual Studio 新建一个工程然后打包的方式来生成一个安装包，不过操作起来比较麻烦，而且生成的安装包也不是很美观。

因此实际上我这里选择了使用 NSIS_SetupSkin 来生成安装包。关于 NSIS_SetupSkin 的使用可以自行查阅。

将 NSIS_SetupSkin 工程可我们的工程放在同级。

把 release 下的所有文件拷贝到  NSIS_SetupSkin/FilesToInstall 下

```python
def b_li(path ,outPath):
    # （root，dirs，files）分别为：遍历的文件夹，遍历的文件夹下的所有文件夹，遍历的文件夹下的所有文件
    global newOutPath
    global newRootPath
    newOutPath = outPath
    newRootPath = path
    for root, dirs, files in os.walk(newRootPath):        
        for file in files:
            if not os.path.exists(newOutPath):
                os.makedirs(newOutPath)
            shutil.copyfile(root + '\\' + file, newOutPath + "\\" + file)
            if showLog == "-v":
                print(root + '\\' + file + ' copy success-> ' + newOutPath + '\\' + file)
        for dir_in in dirs:
            shutil.copytree(root + "/" + dir_in,newOutPath + "/" +dir_in)
            # b_li(newRootPath + "/" + dir_in,newOutPath + "/" + dir_in)
        break
```

然后执行脚本打包即可。具体可以参考最后的附件。

# 拷贝附加文件

当然可以在打包完成生成安装包前通过 pyhton 批量的把文件复制到 release 下。

但实际开发中有一些插件写的比较简单并没有处理 dill 自动打包进应用的操作导致我们在使用的时候需要自己拷贝这些文件到我们应用的同级目录，比如 sqlite 插件需要拷贝 sqlite3.dll 到根目录才能正常使用。

因此实际上我们不光在打 release 包的时候需要拷贝这些文件，在开发 debug 环境下一样需要这些文件，因此这里最好能有一个通用的解决方案。下面就是我想到的一种解决方式 —— 修改 flutter build-tools 在编译期就拷贝这些文件。

当然首先需要熟悉一下执行 flutter build  和 flutter run 的时候 flutter 都做了什么操作。

## flutter tools 简单说明

这里简单的说一下，详细的还请查看具体资料。

当我们执行一个 flutter 命令的时候都对应了 flutterRoot/packages/flutter_tools 下的对应命令，当然实际执行的时候 flutter 为了加快执行速度把 flutter_tools 编译成了快照 flutterRoot/bin/cache/flutter_tools.snapshot。

flutter_tools 的源码在 flutterRoot/packages/flutter_tools/lib/src/ 下， 比如 commands 下每个 dart 文件都对应了一个命令。

以 flutter run 为例，

- 首先 runner/flutter_command.dart 解析一通以后，进入到 run.dart 的 runCommand 方法，

- 然后在其中执行了 runner.run() 对应的就是 HotRunner 活着 ColdRunner 的 run 方法，

- 进入到  run_hot.dart/ run 方法 它做了一通操作以后调用了 device.runHot 方法，这个 device 是一个 FlutterDevice ，进入到其中发现它又执行了 device.startApp 方法， 这个 device 则代表了具体的平台，在桌面平台则是  DesktopDevice ，具体到 widnows 上对应的是 WindowsDevice ，WindowsDevice 继承了 DesktopDevice。

- 进入到 DesktopDevice.startApp 发现 它首先调用了 buildForDevice 方法，这个方法在 WindowsDevice 中有具体实现，它执行了 buildWindows 方法。

    - 进入到 build_windows.dart buildWindows 方法可以看到它实际上就是组装了一堆  Visual Studio 所需要的参数，然后调用 Visual studio 编译 windows 应用。（这也就是为什么我们 build 下编译后的工程是一个 Visual studio 工程，可以直接在 Visual studio 中打开编写对应 c++ 代码。）

    - 执行完 buildWindows 实际上就已经编译出 exe 文件了，接着回到 startApp 继续向下执行， 通过 executablePathForDevice 获取到了 exe 文件的启动命令，然后开始启动命令

- 当启动以后 回到  runHot 方法中启动了一个 stream 监听来链接设备以输出 log 等等操作。

至此一个完整的启动流程就完成了。 flutter build 的流程和 run 大同小异，观察整个流程如果想要在编译期执行我们的拷贝操作，则应该在 windows 编译后同时启动前来拷贝这些文件。

那么就继续回到 build_windows.dart buildWindows 观察一下这个方法。

```dart
Future<void> buildWindows(WindowsProject windowsProject, BuildInfo buildInfo, {
  String? target,
  VisualStudio? visualStudioOverride,
  SizeAnalyzer? sizeAnalyzer,
}) async {
    /// ... 

  final VisualStudio visualStudio = visualStudioOverride ?? VisualStudio(
    fileSystem: globals.fs,
    platform: globals.platform,
    logger: globals.logger,
    processManager: globals.processManager,
  );
    /// ...
  try {
    /// 执行 cmake 编译第三方库
    await _runCmakeGeneration(
      cmakePath: cmakePath,
      generator: cmakeGenerator,
      buildDir: buildDirectory,
      sourceDir: windowsProject.cmakeFile.parent,
    );
    if (visualStudio.displayVersion == '17.1.0') {
      _fixBrokenCmakeGeneration(buildDirectory);
    }
    /// 编译 windows 
    await _runBuild(cmakePath, buildDirectory, buildModeName);
  } finally {
    /// 可以在这里添加一个我们自己的操作
    status.cancel();
  }
  /// ...
}
```

可以看到它组装了一堆参数以后 执行了 runBuild 函数进行 vs 的编译，那么我们就可以在 runBuild 之后执行我们自己的操作。

## 编译期拷贝文件

我们可以在  finally 中添加一段代码执行我们的拷贝操作，

首先在 我们工程的 windows 下添加一个 sdk 文件夹，然后把需要的文件都放入里面，然后我们在  windows 下新建一个 move_file.py 文件用来执行 拷贝操作。

```python
if __name__ == "__main__":
    # 文件夹路径
    base_path = os.path.dirname(os.path.abspath(__file__))
    buildMode = sys.argv[1].capitalize()
    
    # 输出路径
    out_path = os.path.dirname(base_path) + "/build/windows/runner/" + buildMode
    b_li(base_path + "/sdk",out_path)
```

然后在 finally 中添加代码执行这个 拷贝操作

```dart
    final String prebuildScriptPath = globals.fs.currentDirectory.path + '/windows/move_file.py';
    final File scriptFile = globals.fs.file(prebuildScriptPath);
    if (scriptFile.existsSync()) {
      final RunResult ret = await globals.processUtils.run(
        <String>['python', prebuildScriptPath,buildModeName],
        workingDirectory: globals.fs.currentDirectory.path,
      );
    }
```

这样 在编译期我们就可以直接把需要的文件拷贝到对应的文件夹中。

