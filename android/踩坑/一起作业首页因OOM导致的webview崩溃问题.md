# 事件背景

测试反馈首页在刷新的时候有偶尔崩溃的情况，但是情况描述的不是很清楚，因为不是能一直复现的。

## 问题复现

找到测试妹子要来出问题的手机自测。根据测试的描述既然是在刷新的时候崩溃，所以就一直刷新首页看看能不能复现，果然复现了出来，在进行很多次刷新以后首页出现了崩溃，然后再尝试几次并且统计各种数据发现每到第 12 次刷新的时候就出现崩溃。崩溃日志：

![](http://blogqn.maintel.cn/错误.png?e=3109409655&token=cs2nCfx72Y7hW0_NpFYzb3Jab90IJWraRtphMd-q:XLcyvilImEFKd6WEFJKYqK_ZGU8=)


# 坑一 Fatal signal 6 (SIGABRT), code -6 

首先需要说明的是首页是一个 fragment，它的布局是这样的

```xml
<RelativeLayout>
    <SmartRefreshLayout>
        <ObservableNestedScrollView>
            <LinearLayout>
                ...
                <ViewPager>
                    <GridView/>
                </ViewPager>
                ...
            </LinearLayout>
            <FrameLayout>
        </ObservableNestedScrollView>
    </SmartRefreshLayout>
</RelativeLayout>
```

可以看到嵌套很深，而且很复杂又是下拉刷新又是 scrollview 而且 FrameLayout 里面又嵌套了一个 fragment 并且加载了 webView。然后根据上面的错误第一时间想到的是 webView 引起的问题，因为这个错误日志给出的信息很少，只能看出是在 native 层出现了一些问题，网上类似的问题有很多，解决方案也很多，一一实验都没有解决问题。

在这个上面困扰了两三个小时，个人感觉不应该这么诡异，再来梳理代码：

- 被嵌套的 fragment 是一个封装好的专门用来加载 webview 的 fragment
- 被嵌套的 fragment 在很多其他页面也有使用，只不过是没有使用在这么复杂的页面中
- 这里几乎没有对 webview 做任何操作只是做了一个加载而已
- 代码中看不出任何在 webView 中可能出现的问题

干脆做个试验，就单独把这个 fragment 嵌套进一个空白的 fragment 里面，不做其他操作只做和首页一样的逻辑即可，然后进行实验。

既然说是坑了，结果当然是**没有任何问题**。

因为在首页中没有任何其他的业务逻辑有和被嵌套的 fragment 有关联，所以可以确认问题不在这里。那为什么会报这个错误呢？能猜到的就是其他问题引起程序崩溃然后导致 webview 加载的时候出现问题，但是这些崩溃没有被在日志中显示出来。

既然这样就把嵌套 fragment 这一部分代码去掉运行一下看看有什么问题。

# 坑二 Could not read input channel file descriptors from parcel

继续踩坑，把 fragment 这一部分代码去掉运行以后果然发生了变化，同样的刷新次数同样的崩溃但是这次崩溃的日志不一样了：

    java.lang.RuntimeException: Could not read input channel file descriptors from parcel.
    at android.view.InputChannel.nativeReadFromParcel(Native Method)
    at android.view.InputChannel.readFromParcel(InputChannel.java:148)
    at android.view.IWindowSession$Stub$Proxy.addToDisplay(IWindowSession.java:690)
    at android.view.ViewRootImpl.setView(ViewRootImpl.java:502)
    at android.view.WindowManagerGlobal.addView(WindowManagerGlobal.java:259)
    at android.view.WindowManagerImpl.addView(WindowManagerImpl.java:69)
    at android.widget.Toast$TN.handleShow(Toast.java:405)
    at android.widget.Toast$TN$1.run(Toast.java:313)
    at android.os.Handler.handleCallback(Handler.java:733)
    at android.os.Handler.dispatchMessage(Handler.java:95)
    at android.os.Looper.loop(Looper.java:136)
    at android.app.ActivityThread.main(ActivityThread.java:5017)
    at java.lang.reflect.Method.invokeNative(Native Method)
    at java.lang.reflect.Method.invoke(Method.java:515)
    at com.android.internal.os.ZygoteInit$MethodAndArgsCaller.run(ZygoteInit.java:779)
    at com.android.internal.os.ZygoteInit.main(ZygoteInit.java:595)
    at dalvik.system.NativeStart.main(Native Method)

同样也是没有任何有用的信息，不过还是要比之前的要详细一些，随手 google 一下这个问题网上给出的答案几乎一致：

- （1）RemoteView中添加的图片太大了,超过40K会报这个异常
- （2）Intent传递的数据太大了超过1M也会报这个错误
- （3）FileDescripter 太多而且没有关闭,looper太多没有quit
- （4）试试在AndroidManefest.xml中对当前Activity配置configchange=“orientation|keyboardHidden”(不晓得有没有写对)强制在Activity横竖屏切换的时候不重新onCreate。
- （5）谷歌原生BUG很多人都遇到这个问题而且没有得到解决

根据业务逻辑首先排除了1、2、4，实际上5的可能性也不大，那问题可能就是出现在3上面了。

## FileDescripter

FileDescripter 是个什么东西？在官方文档里解释如下：

    Instances of the file descriptor class serve as an opaque handle to the underlying machine-specific structure representing an open file, an open socket, or another source or sink of bytes. The main practical use for a file descriptor is to create a FileInputStream or FileOutputStream to contain it. 

简单来说就是一个在底层的句柄，用来打开文件、套接字或者其他什么什么的东西。它是来自于 linux 的一个概念，每个程序默认可以打开的句柄数量是 1024 个，任何一个 IO 操作都会使用一个 FD。有一些文档还提到一个程序打开的 FD 不会超过 100 个，使用WebView的也不会超过200个,如果到达了500以上基本都存在泄露问题。可以使用命令来确定进程使用的 FD 的数量：

> adb shell lsof | grep <your-pid> | wc -l

既然这样了就查一下吧，打开手机运行命令结果是0！不管运行多少次结果都是0。继续 google 发现这个命令需要 root 权限才行，GG （这里不得不吐槽一下vivo的手机root起来真麻烦）。没办法了只能找来一个测试机 root 以后继续排查，果然发现随着刷新页面打开的句柄数量在暴增：

>adb shell lsof | grep 29344 | wc -l
>123
>adb shell lsof | grep 29344 | wc -l
>195
>...

## 确认问题

经过上面分析最终确认了崩溃的原因，那么回过头来继续看代码，首先确认一下在哪里使用了这个 FileDescripter。根据前面 FileDescripter 的功能然后结合代码可以确定在这个页面中如果需要用到它就只可能出现在加载图片上。这个时候首先想到的问题可能出现在图片加载框架上，因为图片加载及缓存的框架是公司自己封装的基础组件，还是有可能出现一些隐藏 bug 的。

所以不如先来做个试验，写一个简单 demo 一次性加载了上千次图片发现并没有崩溃。所以问题不出在图片加载框架上。而且，首页加载的图片不超过10张，怎么会引起句柄数量过多呢，唯一的可能就是哪里有循环或者多次的重复加载导致的，首页经过代码分析可能出现的地方就是在 listView 或者 gradview 的 adapter的 gitView 方法中，因为如果嵌套过多或者高度问题会导致 getView 方法执行多次。那么就 debug 看看吧。果然发现在其中一个 adapter 的 gietView 方法执行很多次，只加载六张图片的情况下竟然执行了七十多次，这是很不正常的。而 70 多这个数字很有意思，结果之前崩溃的统计 77 * 12 = 924 再加上一些其他地方打开的 FD 数量差不多就是 1024 引发崩溃，那么基本上问题就出现在这里了。

经过上面的分析基本确定了问题出现的地方，但是还没有找到具体出错的代码，不过既然找到了出错的方法也就好办了。因为代码很简单，把图片加载相关的去掉再进行测试果然没有问题。下面就是出错的代码：

```java
// 其实就是一个很简单的图片加载
finalViewHolder.mgifMySelectImg.setImageResource(R.drawable.parent_grow_select_img_default);
```
其实就是一个很简单的图片加载，但是问题出现在这上面，因为 mgifMySelectImg 是一个 GifImageView ，他是一个引用的第三方库[地址](https://github.com/koral--/android-gif-drawable)(当然提前申明新版中这个库的问题已经解决了)。

# 解决

既然知道原因了解决起来也很简单。因为这部分代码不是自己写的，和同事沟通以后把 mgifMySelectImg 修改为 ImageView 解决了问题。

# 后续

当然解决问题很简单，不过在这过程中也发现了一些问题同样要解决。

首先就是 gitView 执行过多的问题，因为它执行次数过多势必会导致页面卡顿，所以做了简单的优化：

- 减少布局层级
- 对 gradView 做了一层封装，判断在 onMeasure 时 getView 及时跳出中不进行资源加载

    关于 getView 的跳出时机需要自己根据需求来定，实测结果如果跳出的时机不对可能会造成布局错乱。因此建议只在耗时的资源加载时做这个判断。

listView 优化就简单说明一下，随手 google 一下有很多，也很详细。

然后就是为什么会出现内存泄露呢，GifImageView 出现内存泄露的问题在哪里？这个没办法只能去追踪源码学习一下也许能避免以后开发中出现此问题，也简单说明一下：

**说明**：GifImageView 版本 1.2.3，根据实测至少 1.2.15 以后版本没有此问题。

在 setImageResource 方法中它调用了 GifViewUtils.setResource 方法。

```java
    static boolean setResource(ImageView view, boolean isSrc, int resId) {
        Resources res = view.getResources();
        if (res != null) {
            try {
                GifDrawable d = new GifDrawable(res, resId);
                if (isSrc) {
                    view.setImageDrawable(d);
                } else if (VERSION.SDK_INT >= 16) {
                    view.setBackground(d);
                } else {
                    view.setBackgroundDrawable(d);
                }

                return true;
            } catch (NotFoundException | IOException var5) {
                ;
            }
        }

        return false;
    }
```

在 setResource 中 new 了一个新的 GifDrawable。在它的构造方法中调用了创建了一个 GifInfoHandle 对象，

```java
    GifInfoHandle(AssetFileDescriptor afd) throws IOException {
        try {
            this.gifInfoPtr = openFd(afd.getFileDescriptor(), afd.getStartOffset());
        } finally {
            try {
                afd.close();
            } catch (IOException var8) {
                ;
            }

        }
    }
```

问题就出在这里 GifInfoHandle 的 openFD 方法上，它是一个 native 方法，由于 github 上没有找到 1.2.3 关于这一部分的 native 代码，所以也就没办法再继续下去了。

那么就到此为止吧，当然这个库还是不错的，它与传统的使用webView 或者 Movie 来加载 gif 图片的方式不同，通过在 native 层来做一些事情的方式来实现。当然具体的原理还没有去研究。

当然在项目中已经把这一个gif加载的库升级到最新，因为其他地方也在使用如果不进行升级肯定存在隐患。

# 总结

到此一个因为 OOM 而引起的爬坑之旅算是结束了，前后花费七八个小时最终的问题解决起来却很简单——不得不说搞开发就是这么奇妙。坑爬完了总要有所收获，这里也简单总结一下，算是一次经验积累吧。

- 遇到奇怪，隐晦的问题的时候不要急，通过删代码的方式能比较好的找到真正出问题的地方；

- 多做实验，把怀疑可能出问题的地方单独拿出来试验一下；

- 准备一个有 root 权限的手机，因为很多时候由于工程的限制没法用模拟器；
  
- 不光要解决问题，更要知道问题的所在。

最后，不要怕爬坑，爬坑的过程中总能学到很多东西。
