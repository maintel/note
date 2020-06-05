关于 1.12 版本 flutter 引擎不能合并入 aar 中是因为 他使用了依赖的方式，


原来的依赖方式

```
                    // Include `libflutter.so`.
                    // TODO(blasten): The libs should be outside `flutter.jar` when the artifacts are downloaded.
                    from(project.zipTree("${flutterRoot}/bin/cache/artifacts/engine/${engineArtifactSubdir}/flutter.jar")) {
                        include 'lib/**'
                    }
```

现在的依赖方式

```
        platforms.each { platform ->
            String arch = PLATFORM_ARCH_MAP[platform].replace("-", "_")
            // Add the `libflutter.so` dependency.
            println "io.flutter:${arch}_$flutterBuildMode:$engineVersion"
            addApiDependencies(project, buildType.name,
                    "io.flutter:${arch}_$flutterBuildMode:$engineVersion")
        }
```

1.12 版本合并 aar 将 flutter 引擎打入最终 aar 的初步思路，将现有的远程依赖方式修改成 jar 包引入的方式，这种方式需要将 flutter 引擎下载下来放入一个特定的文件夹，然后修改 flutter.gradle 中的依赖方式。


```
        addApiDependenciesFile(project,buildType.name,"${flutterRoot}/bin/cache/artifacts/embedding/flutter_embedding_${flutterBuildMode}-${engineVersion}.jar")
        List<String> platforms = getTargetPlatforms().collect()
        // Debug mode includes x86 and x64, which are commonly used in emulators.
        if (flutterBuildMode == "debug" && !useLocalEngine()) {
            platforms.add("android-x86")
            platforms.add("android-x64")
        }
        platforms.each { platform ->
            String arch = PLATFORM_ARCH_MAP[platform].replace("-", "_")
            // Add the `libflutter.so` dependency.
            println "${flutterRoot}/bin/cache/artifacts/embedding/engine/${arch}_${flutterBuildMode}-1.0.0-${engineVersion}.jar"
            // addApiDependencies(project, buildType.name,
            //         "io.flutter:${arch}_$flutterBuildMode:$engineVersion")
            addApiDependenciesFile(project,buildType.name,"${flutterRoot}/bin/cache/artifacts/embedding/engine/${arch}_${flutterBuildMode}-${engineVersion}.jar")
        }
```


```
    // 将远程依赖的方式替换成 jar 包的形式
    void addApiDependenciesFile(Project project, String variantName, Object dependency, Closure config = null){

        String configuration;
        // `compile` dependencies are now `api` dependencies.
        if (project.getConfigurations().findByName("api")) {
            configuration = "${variantName}Api";
        } else {
            configuration = "${variantName}Compile";
        }
        // project.dependencies.add(configuration, dependency, config)
        project.dependencies.add(configuration, project.files(dependency))
    }
```

但是在配合第三方插件使用的时候直接引用 flutter module 会出现依赖重复的问题， 排除了依赖还是不行，等待后续进一步解决。