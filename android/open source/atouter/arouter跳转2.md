# 跳转2 拦截器 返回值等问题

## 拦截器

拦截器的使用很简单，直接创建一个实现 IInterceptor 接口就可以了。例如下面这样


```kotlin
@Interceptor(priority = 10, name = "拦截测试")
class TestInterceptor : IInterceptor {
    override fun process(postcard: Postcard?, callback: InterceptorCallback?) {
        val path = postcard?.path
        callback?.onContinue(postcard)
        if (ACTIVITY_MAIN_TEST == path) {
            callback?.onContinue(postcard)
        } else {
            callback?.onInterrupt(RuntimeException("非法路由"))
        }
    }

    override fun init(context: Context?) {
        println("TestInterceptor 初始化")
    }
}
```

- init 方法会在应用初始化的时候执行
- process 方法里面做具体的拦截操作
- onContinue 和 onInterrupt 必须有一个被执行
- 拦截器的初始化和执行都是在子线程中的
- 注解中的 priority 参数代表了拦截器的优先级，数值越低优先级越高


# 跳转返回

在 navigation 方法中直接添加一个参数实现 NavigationCallback 接口就可以了。

```kotlin

    ARouter.getInstance().build(uri).navigation(this, 100, naviagtion)

    object naviagtion : NavigationCallback {
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
            // 到达
            println("onArrival")
        }
    }
```

onArrival 方法会在执行完 startActivity 后执行，但是也是在目标 activity 的 onCrate 方法之前执行的。

## 当路由丢失时的全局策略

arouter 提供了当路由丢失时的全局处理策略  DegradeService

实现 DegradeService 接口，然后通过 route 随便给一个注解，在 onLost 中做出处理即可。

```kotlin
@Route(path = "/degrade/impl")
class DegradeServiceImpl : DegradeService {
    override fun onLost(context: Context?, postcard: Postcard?) {
        if (context != null)
            context.startActivity(Intent(context, MainActivity::class.java))
    }

    override fun init(context: Context?) {
    }
}
```

需要注意的是，它只有在 callBack 为设置的情况下才会执行，如果是何止了 callBack 则不会执行这个。