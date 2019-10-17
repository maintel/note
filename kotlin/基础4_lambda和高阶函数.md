# 前言

kotlin 在 lambda 的使用上是很频繁的。[官方文档](http://www.kotlincn.net/docs/reference/lambdas.html)，这里主要讲一些使用的方法和一些自己的理解。

# Lambda 表达式

lambda 表达式就是函数的一种表现方式，一个 lambda 表达式其实就相当于一个函数，更准确的讲应该是一个未声明的函数，能够以表达式的形式进行传递。

## 使用 lambda 的好处

- 代码简洁

个人理解 lambda 表达式出现最直观的一个作用就是代码变得更简洁。比如下面的例子

```kotlin
    @Test
    fun test1() {
        var a = { x: Int, y: Int -> x + y }
        println(a(1, 3)) // 4
        println(a(2, 3)) // 5
        println(a(3, 3)) // 6
        var a1 = sum(1, 3)
        var a2 = sum(2, 3)
        var a3 = sum(3, 3)
        println(a1) // 4
        println(a2) // 5
        println(a3) // 6
    }
    
    fun sum(a: Int, b: Int): Int {
        return a + b
    }
```
很明显如果使用 lambda 表达式能够把代码量缩小很多，当然这只是我们看到的最直观的结果，不过这也不失为一个我们选择它的重要理由(*￣(エ)￣)。

- 替代匿名内部类和匿名函数

lambda 表达式还有一个重要的作用是替代匿名内部类和匿名函数，可以参看 java 的 lambda 来说，为什么要替代匿名内部类，首先讲的一点肯定是代码上更简洁，但是这只是其次的，最重要的原因是匿名内部类存在着影响应能的问题。

为什么说匿名内部类会影响性能，首先，编译器会为每一个匿名内部类创建一个类文件。而每一个类在使用之前需要加载类文件并进行验证，这个过程则会影响应用的启动性能。类文件的加载很有可能是一个耗时的操作，这其中包含了磁盘IO和解压JAR文件。随着匿名内部类进行加载，其必然要占用JVM中的元空间（从Java 8开始永久代的一种替代实现）。如果匿名内部类的方法被JIT编译成机器代码，则会存储到代码缓存中。同时，匿名内部类都需要实例化成独立的对象。以上关于匿名内部类的种种会使得应用的内存占用增加。

注意的一点就是 kotlin 的 lambda 表达式和 java 的 lambda 在语法上是有区别的，但是他们设计的初衷都是一样的。

## lambda 的使用

kotlin 中 lambda 的语法有以下几点

首先，lambda 表达式总在花括号中`{}`，完整的语法声明也应该放在其中，并有可选的类型标注， 函数体跟在一个 `->` 符号之后。如下：

```kotlin
var a = { x: Int, y: Int -> x + y }  //完整语法
var b: (Int, Int) -> Int = { x, y -> x + y } // 这种写法和 a 等价
var c = { x: String -> println(x) }  //无返回值
var d: (String) -> Unit = { x -> println(x) } // 这种写法和 c 等价

```
其次，如果只有一个参数，它允许我们不声明唯一的参数，并且隐式的声明为 it，所以上面例子中 c d 的写法可以如下：

```kotlin
var e: (String) -> Unit = { println(it) } // 这种写法和 c d 等价
```
还有，如果推断出的该 lambda 的返回类型不是 Unit，那么该 lambda 主体中的最后一个（或可能是单个）表达式会视为返回值。甚至可以写在 if else 等这样的语句中，这个写法也很有用我们可以不用手动去写 return

```kotlin
        var f = { x: Int, y: Int ->
            if (x > y) {
              println(x)
                x  //返回 x
            } else {
              println(y)
                y //返回 y
            }
        }
```

当然也可以使用限定返回语法显式的返回一个值比如：

```kotlin
observable.distinct { t ->
          when {
              t < 3 -> return@distinct "a"
              t in 3..4 -> return@distinct "b"
              else -> return@distinct "c"
          }
      }
```

然后在 lambda 的使用时，如果自定义一些函数想要接收表达式作为参数就不得不使用高阶函数。

# 高阶函数

高阶函数是将函数用作参数或返回值的函数。官方例子讲的很清楚 lock() 函数。

```kotlin
fun <T> lock(lock: Lock, body: () -> T): T {
    lock.lock()
    try {
        return body()
    }
    finally {
        lock.unlock()
    }
}
```
分析上面的这个函数，发现它接收的参数中第一个参数是一个 Lock 对象，第二个参数是 body 一个表达式 ()-> T，根据上面的 lambda 的语法可以知道它是一个不带参数并且返回 T 类型值的函数，而 lock() 函数也返回 T，可以看到在 try 中直接把 body 函数作为返回值返回了。**这里就提现出来了 lambda 表达式可以作为参数传递**

高阶函数的好处是显而易见的，它可以降低我们代码的复杂度，使我们的代码变得简洁。就比如下面的代码，如果使用高阶函数代码量会减少很多。

```kotlin
    @Test
    fun test4() {
        higher(9, { t -> "aaaa::$t" })
        var a = 9
        normal(a, getString(a))
    }

    fun getString(a: Int): String {
        return "nnn$a"
    }

    fun normal(a: Int, b: String) {
        if (a > 10) {
            println(b)
        } else {
            println("nnnn:$b")
        }
    }
    //使用高阶函数 一个函数就搞定了
    fun higher(a: Int, b: (a: Int) -> String) {
        if (a > 10) {
            println(b(a))
        } else {
            println("aaaa:${b(a)}")
        }
    }
```

## 接受一个可为空的表达式参数

和一般参数一样，高阶函数作为参数的时候一样可以为空，例如：

```kotlin
    fun loadMoreData(e: (() -> Unit)?) {
        refreshData(page).observeOn(AndroidSchedulers.mainThread())
                .subscribeOn(Schedulers.newThread())
                .subscribe({
                    e?.invoke()
                    refreshView(it)
                }, {
                    e?.invoke()
                })
    }
```

以上就是关于 lambda 和 高阶函数的全部内容。仅仅是一些个人理解和总结，错误疏漏之处还请指出。

**参考**

*[深入探索Java 8 Lambda表达式](http://blog.oneapm.com/apm-tech/226.html)*
*[细说 Kotlin 的 Lambda 表达式](https://juejin.im/entry/58a382da61ff4b0058ab4542)*
*[官方文档](http://www.kotlincn.net/docs/reference/lambdas.html#%E9%AB%98%E9%98%B6%E5%87%BD%E6%95%B0)*