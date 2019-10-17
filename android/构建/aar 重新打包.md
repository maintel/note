

# aar 重新打包

- 修改后缀名 解压 aar
- 解压 classes.jar 文件
- 修改该 class 文件
- 重新打包 classes 成为 jar 包
    
    >jar cvf newClasses.jar -C 文件夹名/ .

- 替换掉 classes.jar
- 重新打包 aar
    >jar cvf newAAR.aar -C 文件夹名/ .

# 修改 class 文件的方式

网上很多说使用 jg-gui 的方式，其实可以通过下面这种方式来做，

在 Android stuido 中找到要修改的类例如 b.class，然后在工程下建一个一摸一样的类 b.java （包名什么的都要一致），把 b.class 中的内容复制到 b.java 中，然后 rebuild 一下工程就可以了。

如果遇到错误，比如找不到类，但是这个类确确实实已经引用了，那么可以直接写类的全名例如：

```java

import com.rjsz.frame.pepbook.b.b;

b = new b()  // 编译时这个地方报错

```

可以修改成下面这种方式：

```java
b = new com.rjsz.frame.pepbook.b.b()
```

然后在 `moduleName\build\intermediates\debug\包名` 下找到对应的 class 文件，将原有 jar 中的 class 文件替换就可以了。

关于替换有两种方式：

- 用解压软件打开 jar（并不是解压出来是打开），然后将原有的 class 文件删除，从上面文件夹中将class 文件复制进去就可以了。
- 用解压软件解压 jar ，然后在资源管理器中将 class 文件替换完，这里看到的 class 可能有多个，例如 b.class 可能有很多 b$ 开头的文件，都复制进去就可以了，然后使用 `jar cvf newClasses.jar -C 文件夹名/ .` 重新打包就可以了