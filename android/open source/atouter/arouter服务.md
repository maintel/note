# ARouter 通过依赖注入解耦

ARouter 提供了通过注解及接口的方式来暴露服务，以达到模块间解耦的目的。它在项目中不是必须的，更像是一种在模块间解耦的思想。

先说一下大概思想就是通过一个公共的接口，然后向同一个中心来注册，然后达到在不同模块间访问的目的。

下面就一步一步研究一下这个东西。

## 使用

### 声明接口

个人认为接口最好声明在公共模块当中，这样各个模块间都能进行友好的使用

```kotlin
interface TestService : IProvider {

    fun test(str: String): String

    fun getdata(): String

}
```

### 实现接口

比如在主 module 中实现它：

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

在主 activity 中给它提供数据

```kotlin
class MainActivity : AppCompatActivity() {

    @Autowired(name = "/serviceTest/test")
    @JvmField
    public var testService: TestServiceImpl? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        testService?.data = "隔壁老王"
    }
```

### 在其他模块访问数据

然后就可以在其他模块中访问 TestServiceImpl 所提供的数据：

**下面这个 activity 是在另外一个 module 中的**

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

然后可以看到

![](http://blogqn.maintel.cn/TIM截图20181127152845.png?e=3120103766&token=cs2nCfx72Y7hW0_NpFYzb3Jab90IJWraRtphMd-q:eMcQmnwYBH4P4YACziAbCWwU6BQ=)

在子 module 中得到了主 module 提供的数据，同时看起来这两个 module 之间没有任何的耦合关系，从而达到了彻底的解耦。这样的好处是显而易见的。

## 原理

首先就是在主工程中的自动注入的时候，最终会走到下面的关键方法，它把初始化的类放到了一个 Warehouse.providers 中，这个是一个静态的 map 用于全局的存放各个服务类。

关键代码：

```java
public class LogisticsCenter {

    public synchronized static void completion(Postcard postcard) {
            switch (routeMeta.getType()) {
                case PROVIDER:  // if the route is provider, should find its instance
                    // Its provider, so it must implement IProvider
                    Class<? extends IProvider> providerMeta = (Class<? extends IProvider>) routeMeta.getDestination();
                    IProvider instance = Warehouse.providers.get(providerMeta);
                    if (null == instance) { // There's no instance of this provider
                        IProvider provider;
                        try {
                            provider = providerMeta.getConstructor().newInstance();
                            provider.init(mContext);
                            Warehouse.providers.put(providerMeta, provider);
                            instance = provider;
                        } catch (Exception e) {
                            throw new HandlerException("Init provider failed! " + e.getMessage());
                        }
                    }
                    postcard.setProvider(instance);
                    postcard.greenChannel();    // Provider should skip all of interceptors
                    break;
                case FRAGMENT:
                    postcard.greenChannel();    // Fragment needn't interceptors
                default:
                    break;
            }
        }
    }
}
```


```java
class Warehouse {
    static Map<Class, IProvider> providers = new HashMap<>();
}
```

同时在子 module 中根据路径来获取服务的时候，也会走到上面的代码中，这个时候就能从里面得到想要的服务类，从而得到数据。

从上面的原理也能看出一个问题，就是提供数据的实现类必须通过 ARouter 提供的方法来初始化，否则在子 module 去获取的时候是获取不到的。

ARouter 提供的初始化方法如下：

```java
	 // 1. (推荐)使用依赖注入的方式发现服务,通过注解标注字段,即可使用，无需主动获取
	 // Autowired注解中标注name之后，将会使用byName的方式注入对应的字段，不设置name属性，会默认使用byType的方式发现服务(当同一接口有多个实现的时候，必须使用byName的方式发现服务)
    @Autowired
    HelloService helloService;

    @Autowired(name = "/yourservicegroupname/hello")
    HelloService helloService2;

    // 2. 使用依赖查找的方式发现服务，主动去发现服务并使用，下面两种方式分别是byName和byType
	helloService3 = ARouter.getInstance().navigation(HelloService.class);
	helloService4 = (HelloService) ARouter.getInstance().build("/yourservicegroupname/hello").navigation();
```
