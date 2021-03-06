
[Upload](https://ant.design/components/upload-cn/)

# 自定义上传

一般情况下使用 upload 来上传文件时都是异步的，官方默认的也是这样的，关于异步上传的参数问题还没有研究。

现在情景是这样的，接口提供方要求所有要上传的文件转成 base64，放在 get 请求中最后一次性提交。

## 错误的实现

在实现过程中首先想到的是设置 action=''，然后在 onChange 中 status='done' 时对文件进行处理，比如保存下文件列表等。

这样实现貌似没有问题，本地调试的时候也没有看出问题，但是放在服务器上时就出问题了。

当提交的文件比较大时出现提交错误，不能选择成功。用开发者工具查看出现了访问服务器网络错误，为什么没有进行提交设置也进行了提交操作呢。

按照需求来说，当文件选择完毕以后所有的东西应该都还在本地才对，而不应该已经进行了提交。

查看网络发现每选择一个文件，就会对服务器的根目录做一次 post 的提交，当文件较大时时长太长就出现了错误。

看来设置 action='' 是不对的。

## 应该怎么做

查看官方文档可以看到它提供了一个 customRequest 来覆盖默认的上传行为。那么就可以通过它来实现。

~~由于这里不进行上传操作，所以给了 customRequest 一个空的函数，注意不能设置成 null，否则会无效。~~

这里不能给 customRequest 设置成空函数，应该设置相应的值然后手动调用 onSuccess，所以下面的说法也是错误的。

## 问题

~~但是这个时候发现不能对进度条的进度做控制，不知道是不是版本的问题，因为没有了默认的上传行为，进度条一直在转圈圈，然后在 customRequest 中对 onSuccess 进行回调也不会有效果，查看源码的时候感觉应该是有效果的才对。~~

~~最后做了一个取巧的办法，在 onChange 中手动对上传状态进行了改变，这时候 onChange 的 status='done' 被回调了好几次。~~

所以这个时候不能在 onChange 的 status='done' 来做处理，应该在 onSuccess 中做处理。

值得说明的是，在 customRequest 中对 onSuccess 进行回调是会回调 onSuccess 的，但是它不会影响 onChange。其实源码中是有影响到的，可以说明的大概就是 这两个 onSuccess 不一样。


