# 上传到本地仓库

首先配置本地仓库的位置，打开 mavenRoot\conf\settings.xml，然后在 settings 下添加：

    <localRepository>F:/MavenRepository</localRepository>

就可以了。如果不设置，则默认仓库位置在 C:\Users\yourName\.m2\repository。

执行命令上传到本地仓库：

    mvn install:install-file -DgroupId=com.maintel.3dparty -DartifactId=aar-release -Dversion=1.0.9 -Dpackaging=aar -Dfile=filePath

命令说明：

    mvn install:install-file 
    -DgroupId=包名 
    -DartifactId=项目名 
    -Dversion=版本
    -Dpackaging=类型（jar包就是jar，aar就是aar）
    -Dfile=需要上传的包所在位置


# 上传到远程仓库

同样需要在 settings.xml 文件中配置账号，同样打开 mavenRoot\conf\settings.xml，然后在 settings/servers 标签下添加： 

    <server>
      <id>thirdparty</id>
      <username>admin</username>
      <password>admin</password>
    </server>

执行命令：

    mvn deploy:deploy-file -DgroupId=com.maintel.3dparty -DartifactId=aar-release -Dversion=2.1.0 -Dpackaging=aar -Dfile=filePath -Durl=http://maven.yuming.net/nexus/content/repositories/thirdparty/ -DrepositoryId=thirdparty

命令说明：

    mvn deploy:deploy-file 
    -DgroupId=包名 
    -DartifactId=项目名 
    -Dversion=版本
    -Dpackaging=类型（jar包就是jar，aar就是aar）
    -Dfile=需要上传的包所在位置
    -Durl=远程仓库的位置
    -DrepositoryId=仓库ID  // 注意这个 ID 要和上面 server 配置的 ID 一样

# 使用 gradle 脚本上传 aar 包



# gradle 引用本地仓库

```gradle

buildscript {
    repositories {
        mavenLocal()
    }
}

allprojects {
    repositories {
        mavenLocal()
    }
}
````

同样的要在 mavenRoot\conf\settings.xml 中配置好本地仓库的路径