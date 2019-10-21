插件中是能够正常加载宿主中的 so 的，但是经过实测发现使用 system.loadlibrary 的方式加载 so 不成功

原因是插件在通过 loadlibrary 加载 so 的时候去找了插件的 libs 文件夹如：`nativeLibraryDirectories=[/data/user/0/com.pakename.jzt/app_plugins_v3_libs/pointread-10-10-99, /system/lib, /vendor/lib]]]` 但是宿主的 so 文件明显的不在这个文件夹中放着，所以会出现找不到的情况。

可以通过 System.load 的方式来加载 so 文件，这个时候要传入 so 的绝对路径，Android 中获取宿主的 so 路径可以使用下面的方式：

```java
            String nativeLibraryDir = ContextProvider.getApplicationContext().getApplicationInfo().nativeLibraryDir;
            System.out.println("nativeLibraryDir::" + nativeLibraryDir);
            if (nativeLibraryDir != null) {
                System.load(nativeLibraryDir + "/libso.so");
            }
            
```

`ContextProvider.getApplicationContext()` 为获取宿主的 application 对象。