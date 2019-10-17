
<!-- TOC -->

- [安装依赖包报错 ENOENT: no such file or directory" on .DELETE](#安装依赖包报错-enoent-no-such-file-or-directory-on-delete)

<!-- /TOC -->
# 安装依赖包报错 ENOENT: no such file or directory" on .DELETE

解决办法：

    删除 package-lock.json 文件

可以在 npm 官方找到此错误的 [issues](https://github.com/npm/npm/issues/17444)