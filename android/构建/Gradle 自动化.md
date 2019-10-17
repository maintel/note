# 任务结束后版本号自增

**版本：** 
    gradle-w:4.10.1

    com.android.tools.build:gradle:2.3.2

这里是直接修改了 properties 文件。

```
gradle.projectsEvaluated {
    assembleRelease.doLast {
        syncProperties()
    }
}

def syncProperties() {
    def versionCodeFile = new File('gradle.properties')
    if (versionCodeFile.canRead()) {
        Properties properties = new Properties()
        properties.load(new FileInputStream(versionCodeFile))
        def skinVersion = properties['skin_version'].toInteger()
        println(skinVersion)
        properties['skin_version'] = (++skinVersion).toString()
        properties.store(versionCodeFile.newWriter(), null)
    } else {
        throw new GradleException("无法读取version_code.properties文件！")
    }
}
```

# 计算MD5

**版本：** 
    gradle-w:4.10.1

    com.android.tools.build:gradle:2.3.2

```gradle
def calcMD5(File file) {
    MessageDigest md = MessageDigest.getInstance("MD5")
    file.eachByte 4096, { bytes, size ->
        md.update(bytes, 0, size)
    }
    return md.digest().collect { String.format "%02x", it }.join()
}
```