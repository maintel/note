
>文章内容是在 ARouter [官方文档](https://github.com/alibaba/ARouter/blob/master/README_CN.md) 基础上做了补充以及完善，所以会出现大量的重复。

# ARouter

## 什么是 ARouter？

    一个用于帮助 Android App 进行组件化改造的框架 —— 支持模块间的路由、通信、解耦

github地址：https://github.com/alibaba/ARouter

## 为什么需要路由？

Android 本身是提供了页面间跳转的比如 startActivity 以及 Uri 的方式等，但是这些方式在一些场景下不够灵活。比如：

- 在推送需要打开特定页面的情况下，需要很灵活的能跳转到相应的页面，这个时候如果有完整的路由系统，则跳转到任何页面都不成问题（当然通过反射的形式进行跳转也不是不可以）；
- 在多 module 的情况下，如果没有路由系统模块间跳转是很麻烦的一件事情，引入路由系统能很好地做到模块间解耦；
- 有了完整的路由系统我们就可以统一的对跳转做处理，比如打点，拦截等等；

## 为什么是 ARouter？

下面摘抄自 ARouter 官方文档：

- 支持直接解析标准URL进行跳转，并自动注入参数到目标页面中
- 支持多模块工程使用
- 支持添加多个拦截器，自定义拦截顺序
- 支持依赖注入，可单独作为依赖注入框架使用
- 支持InstantRun
- 支持MultiDex(Google方案)
- 映射关系按组分类、多级管理，按需初始化
- 支持用户指定全局降级与局部降级策略
- 页面、拦截器、服务等组件均自动注册到框架
- 支持多种方式配置转场动画
- 支持获取Fragment
- 完全支持Kotlin以及混编
- 支持第三方 App 加固(使用 arouter-register 实现自动注册)
- 支持生成路由文档

# ARouter 使用

## 配置

java 和 kotlin 的配置方式不太一样，java 的配置方式：

```gradle
android {
    defaultConfig {
        ...
        javaCompileOptions {
            annotationProcessorOptions {
                arguments = [AROUTER_MODULE_NAME: project.getName()]
            }
        }
    }
}

dependencies {
    // 替换成最新版本, 需要注意的是api
    // 要与compiler匹配使用，均使用最新版可以保证兼容
    compile 'com.alibaba:arouter-api:x.x.x'
    annotationProcessor 'com.alibaba:arouter-compiler:x.x.x'
    ...
}
```

如果使用 kotlin 则需要下面这样配置：

```gradle
apply plugin: 'kotlin-kapt'

kapt {
    arguments {
        arg("AROUTER_MODULE_NAME", project.getName())
    }
}

dependencies {
    compile 'com.alibaba:arouter-api:x.x.x'
    kapt 'com.alibaba:arouter-compiler:x.x.x'
    ...
}
```
## 混淆

    -keep public class com.alibaba.android.arouter.routes.**{*;}
    -keep public class com.alibaba.android.arouter.facade.**{*;}
    -keep class * implements com.alibaba.android.arouter.facade.template.ISyringe{*;}

    # 如果使用了 byType 的方式获取 Service，需添加下面规则，保护接口
    -keep interface * implements com.alibaba.android.arouter.facade.template.IProvider

    # 如果使用了 单类注入，即不定义接口实现 IProvider，需添加下面规则，保护实现
    # -keep class * implements com.alibaba.android.arouter.facade.template.IProvider

## 初始化以及简单跳转

### 初始化

推荐在 Application 中进行初始化。

```kotlin
    private fun initARouter() {
        if (BuildConfig.DEBUG) {
            ARouter.openLog()
            ARouter.openDebug()
        }
        ARouter.init(this)
    }
```

推荐在开发的时候打开开发开关，这样能看到详细的类扫描结果，并且每次都会重新扫描是否有新增的类，否则可能出现新增了类却找不到的情况。

### 简单跳转

简单的两步，在需要跳转的 activity 上增加注解

```kotlin
//路径必须为两级，第一级是可以重复的，代表了组名

@Route(path = "/main/mainActivityTest")
class MainTestActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val textView = TextView(this)
        textView.text = "TestActivity"
        setContentView(textView)
    }
}
```

使用 navigation 方法进行简单跳转：

```kotlin
    //简单跳转
    ARouter.getInstance().build("/main/mainActivityTest").navigation()
    //（不推荐）即使手动指定了组名，也要给出全路径 否则会找不到类
    ARouter.getInstance().build("/main/mainActivityTest", "main").navigation()
```

由于 ARouter 的路由加载机制是按组加载的，只有当一组中某一个路由被访问了，这个组的路由才会被加载到内存中，所以一样要做好分组工作。

### 传递参数

同时也可以在跳转过程中携带相应的参数，和使用 intent 类似，目标 activity 接收和使用 intent 相同：

```kotlin
    ARouter.getInstance().build("/main/mainActivityTest")
            .withString("test", "传递一个字符串过来")
            navigation(this, naviagtion)
```

ARouter 支持多种类型的参数，可以看做和 intent 一样:

![](http://blogqn.maintel.cn/TIM截图20181122171334.png?e=3119678170&token=cs2nCfx72Y7hW0_NpFYzb3Jab90IJWraRtphMd-q:w02Cgeb1qqZwN3-ZhthSp4R16O4=)

## 使用 URL 进行跳转

ARouter 一样支持通过 URL 来进行跳转，个人感觉这个最好的应用场景就是通过一个 host 和 scheme 来做一个 activity 跳转的中间页，然后通过 ARouter 自动解析 scheme 中的 path 来再次跳转，这样就不用在 AndroidManifest 中对多个 activity 进行添加。


假设有一个中间页面它的清单文件注册如下：

```xml
<activity android:name=".activity.SchemeActivity">
	<!-- Schame -->
	<intent-filter>
	    <data
		android:host="m.maintel.cn"
		android:scheme="arouter"/>

	    <action android:name="android.intent.action.VIEW"/>

	    <category android:name="android.intent.category.DEFAULT"/>
	    <category android:name="android.intent.category.BROWSABLE"/>
	</intent-filter>
</activity>
```

模拟通过 scheme 跳转到它，然后通过它再进行转发：

```kotlin
    val uri = Uri.parse("arouter://m.maintel.cn/test/schameTest")

    ARouter.getInstance().build(uri).navigation(this, 100, naviagtion)
```

注册一个 path 为 `/test/schameTest` 的 activity，则会自动跳转到指定的 activity，ARouter 会自动解析 Url 路径中的 path 来跳转。但是 ARouter 本身不支持通过 URI 来进行隐式的跳转。

## 解析参数

ARouter 支持通过注解的方式自动对字段进行赋值。

声明字段，并添加 @Autowired 注解，ARouter 就能自动的对跳转中的参数进行解析，并对这些字段自动赋值。支持通过 api 或者 URL 的形式传递。

```kotlin
// 目标 activity

@Route(path = "/test/schameTest")
class SchameTestActivity : AppCompatActivity() {
    
    // 可以手动指定名称，如果不指定 name 则默认为字段名
    @Autowired(name = "name")
    @JvmField
    public var account = ""
    @Autowired
    @JvmField
    public var age = 0
    @Autowired
    @JvmField
    public var student: Student? = null
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // 如果要自动注入，必须添加这一行代码
        ARouter.getInstance().inject(this)
        val textview = TextView(this)
        textview.text = "$account::$age::student::${student.toString()}"
        setContentView(textview)
    }
}
```

在 Kotlin 中使用的时候注意在字段上加上 @JvmField 注解，否则即使指定了 public 也无法编译通过，因为在 Kotlin 中 public 的含义和 java 中是不同的。

### 解析 URL 中的参数

用URL跳转比如可以这样：

```kotlin
    val uri = Uri.parse("arouter://m.maintel.cn/test/schameTest?name=maintel&age=100" +
                    "&student={name:\"老王\",age:20}")

    ARouter.getInstance().build(uri).navigation()
```

如果要在 URL 中传递 Obj 则需要使用 json 形式的，并且需要自定义 json 解析器。也很简单只要实现 SerializationService 接口即可，使用方式如下：

```kotlin
// path 为任意即可，同时要注意的是解析器只能有一个，如果定义了多个，则只有一个会生效。
@Route(path = "/jsonService/json")
class JsonServiceImpl : SerializationService {
    override fun <T : Any?> json2Object(input: String?, clazz: Class<T>?): T {
        return Gson().fromJson(input, clazz)
    }

    override fun init(context: Context?) {

    }

    override fun object2Json(instance: Any?): String {
        return Gson().toJson(instance)
    }

    override fun <T : Any?> parseObject(input: String?, clazz: Type?): T {
        return Gson().fromJson(input, clazz)
    }
}
```

URL 中是不能传递 Parcelable 类型的数据的，如果想要传递就需要 API 来传递。

### 使用 API 传递参数

API 的传递参数的方法在上面简单说明了已经，链式的调用 .withxxx 即可。

```kotlin
            ARouter.getInstance().build("/test/schameTest")
                    .withString("name", "maintel")
                    .withInt("age", 100)
                    .withObject("student", Student("老王", 20))
                    .navigation()
```

不过要**注意**的是，如果使用了 withObject 方法，则也需要如使用 URL 的方式一样，定义一个解析器，否则不能传递数据并引起崩溃。

还有一点要注意的是，在使用 URL 进行跳转的时候，即使不需要自动注入，那么可以不写 `        ARouter.getInstance().inject(this)` 代码，但是在字段名上也要加上 `@Autowired` 注解，否则即使通过 intent 一样获取不到想要的数据。

## 拦截器

使用拦截器可以在使用 ARouter 跳转的过程中进行一些处理，比如打点，检测登录状态等等。使用也很简单，实现 IInterceptor 接口，然后加上 @Interceptor 即可：

```kotlin
@Interceptor(priority = 10, name = "拦截测试")
class TestInterceptor : IInterceptor {
    override fun process(postcard: Postcard?, callback: InterceptorCallback?) {
        if (notLoging) {
            // 继续执行跳转
            callback?.onContinue(postcard)
        } else {
            // 抛出一个异常拦截掉登录，或者跳转到特定页面
//            callback?.onContinue(ARouter.getInstance().build("/login/loginActivity"))
            callback?.onInterrupt(RuntimeException("非法路由"))
        }
    }

    override fun init(context: Context?) {
        println("TestInterceptor 初始化")
    }
}
```
使用时要注意：

-  `callback.onContinue` 或者 `callback.onInterrupt` 必须有一个要被调用；
-  拦截器可以设置多个，可以通过 priority 指定优先级，数值越低优先级越高，越先执行；
-  拦截器是在子线程中执行的；
-  可以使用`ARouter.getInstance().build("/home/main").greenChannel().navigation();`跳过所有拦截器

## 跳转结果及全局策略

ARouter 支持在跳转过程中对跳转结果的回调，我们可以自己处理这些回调：

```kotlin
        ARouter.getInstance().build(ACTIVITY_MAIN_TEST).navigation(this, object : NavigationCallback {
            override fun onLost(postcard: Postcard?) {
                // 未找到路由
                println("onLost")
            }

            override fun onFound(postcard: Postcard?) {
                //找到路由
                println("onFound")
            }

            override fun onInterrupt(postcard: Postcard?) {
                // 被拦截
                println("onInterrupt")
            }

            override fun onArrival(postcard: Postcard?) {
                // 到达  到达会在目标 activity 的 onCreate 之前执行
                println("onArrival")
            }
        })
```

同时也可以全局的处理未找到路由的情况，实现 DegradeService 接口，并且给一个任意路由即可，这样我们就能全局的对未找到路由的情况进行处理，而且它的优先级是要比在跳转时指定的回调低的，即如果在跳转时指定了跳转结果的回调，则不会再走全局的处理方法。

```kotlin
@Route(path = "/degrade/impl")
class DegradeServiceImpl : DegradeService {
    override fun onLost(context: Context?, postcard: Postcard?) {
        // 要注意的是这里的 context 可能为 null，它和 ARouter..navigation() 中传递的 context 是同一个。
        ARouter.getInstance().build(ACTIVITY_MAIN).navigation()
    }

    override fun init(context: Context?) {
    }
}
```

## 通过依赖注入解耦：服务管理

这里说的服务，并不是 Android 四大组件中的 service，而是ARouter 提供的一种接口，通过实现这个接口并提供路由，然后通过 ARouter 可以实现在不同模块间进行数据交互以及通讯的功能。简单的使用就想下面这样：

声明接口，并继承自 IProvider
```kotlin
interface TestService : IProvider {

    fun test(str: String): String

    fun getdata(): String
}
```

实现接口：

```kotlin
@Route(path = "/serviceTest/test", name = "test service")
class TestServiceImpl : TestService {

    var data = ""

    override fun test(str: String): String {
        return "TestServiceImpl::$str"
    }

    override fun getdata(): String {
        return data
    }

    override fun init(context: Context?) {
        println("TestServiceImpl init")
    }
}
```

在某个 Activity 中初始化 TestServiceImpl，并提供数据：

```kotlin
        val testService = ARouter.getInstance().build("/serviceTest/test").navigation() as TestServiceImpl
        testService.data = "隔壁老王"
```

然后在另外某个地方就能通过同样的方式来获取数据:

```kotlin
@Route(path = PARENT_ACTIVITY_MAIN)
class ParentMainActivity : AppCompatActivity() {

    @Autowired(name = "/serviceTest/test")
    @JvmField
    public var testService: TestService? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        ARouter.getInstance().inject(this)
        val textView = TextView(this)
        textView.text = testService?.getdata()
        setContentView(textView)
    }
}
```

可以看到上面两个 activity 之间没有任何关联，但是通过 ARouter 提供的服务，两者完成了数据交互。

需要注意的是在服务设置数据以及获取数据的时候必须使用 ARouter 提供的方式来获取实例，否则达不到效果。ARouter 提供了多种方式来获取服务的实例：

```kotlin
    @Autowired
    HelloService helloService;
    //如果一个接口有多个实现的话，必须通过路由的方式来获取
    @Autowired(name = "/yourservicegroupname/hello")
    HelloService helloService2;

    helloService3 = ARouter.getInstance().navigation(HelloService.class);
	helloService4 = (HelloService) ARouter.getInstance().build("/yourservicegroupname/hello").navigation();
```

以上基本上就是 ARouter 使用的全部内容了，总体来说使用还是非常简单方便的，而且并没有什么坑的地方，值得使用。

# 参考

- [ARouter 官方文档](https://github.com/alibaba/ARouter/blob/master/README_CN.md)



