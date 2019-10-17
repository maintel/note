# 前言

之前学习了 lambda 和高阶函数，然后在 android 开发中对 onClick 事件进行监听是一个很常用的功能，kotlin 的常规实现如下：

```kotlin
    rootView.setOnClickListener { view ->
        println("点击了这个ID=${view.id}的view")
    }
```
然后在开发中不可避免的我们也要写一些自定义监听之类的代码。这个时候如果还用 java 的思想去实现的话就有点舍近求远了。

# java 思想实现

在 java 中我们一般的做法是这样的

- 定义一个接口
- 定义一个接口类型变量
- 定义一个 set 方法
- 调用 set 方法设置接口的实现类

用 kotlin 实现就是如下

```kotlin
class MyView{
    //定义一个接口
    interface IOnLabelCheckedListener {
        fun onLabelCheck(label: String)
    }
    //定义一个接口类型变量
    private lateinit var onLabelChecked: IOnLabelCheckedListener

    private fun initView(context: Context) {
        view.setOnCheckedChangeListener { radioGroup, i ->
            if (::onLabelChecked.isInitialized) {
                //接口调用
                onLabelChecked.onLabelCheck(radioGroup.findViewById<RadioButton>(i).text.toString())
            }
        }
    }
    //定义一个 set 方法
    fun setOnLabelCheckedListener(e: IOnLabelCheckedListener) {
        this.onLabelChecked = e
    }
}

      // 调用set方法，通过匿名内部类实现
        MyView.setOnLabelCheckedListener(object : LabelBarView.IOnLabelCheckedListener {
            override fun onLabelCheck(label: String) {

            }
        })
```

## 这样实现的问题

当然是太复杂了。而且最初的时候这样写一时搞不明白为什么 `MyView.setOnLabelCheckedListener` 方法内部不能传入 lambda 表达式，lambda 表达式的存在不就是为了替代匿名内部类嘛。而且如果这个接口定义的是一个 java 类型的接口就是可以用 lambda 表达式的。这是为什么？最后猜想是因为 kotlin 在和 java 互相调用的时候中间又包裹了一层，而我们直接使用 kotlin 来定义这个接口不存在中间这一层就而我们定义的 set 方法又不是一个高阶函数，当然不能使用 lambda 表达式。

下面就用 kotlin 的思想来实现回调

# kotlin 思想实现

kotlin 和 java 有一个重要的不同就是函数式编程。在函数式编程的思想中函数式一等公民，在使用 kotlin 时我们要多利用这种思维来编程。

首先，能想到的就是函数传递，我们要用 lambda 来替代掉匿名内部类可以这样来实现

```kotlin
//从最基础的开始做，把匿名内部类通过 lambda 实现
MyView.setOnLabelCheckedListener(object : MyView.IOnLabelCheckedListener {
        override fun onLabelCheck(label: String) {
          println(label)
        }
})
// 首先 MyView.IOnLabelCheckedListener 中只有一个方法 onLabelCheck(label: String)
// 因此可以写出 lambda 表达式如下
var lam: (String) -> Unit = { label -> println(label) }
```

然后，需要把写好的 lambda 传递进去，这个时候就要求 `setOnLabelCheckedListener` 方法是一个高阶函数

```kotlin
    // 这里接收一个 上面我们改造好的表达式 lam ,它内部实现应该是把 e 赋值给当前类的一个对象
    fun setOnLabelCheckedListener(e: (String) -> Unit) {
       this.lisenter = e
    }
  
    //显然 lisenter 就应该是这样的
    lateinit var linsnter: (String) -> Unit
```

最后使用 linsnter 进行回调

```kotlin
    private fun initView(context: Context) {
       view.setOnCheckedChangeListener { radioGroup, i ->
            linsnter(radioGroup.findViewById<RadioButton>(i).text.toString())
        }
    }
```

最终代码结果：

```kotlin
class MyView{
  lateinit var linsnter: (String) -> Unit

  private fun initView(context: Context) {
       view.setOnCheckedChangeListener { radioGroup, i ->
            linsnter(radioGroup.findViewById<RadioButton>(i).text.toString())
        }
  }

  fun setOnLabelCheckedListener(e: (String) -> Unit) {  
    this.lisenter = e
  }
}
    // 调用时将变量 lam 省略，直接使用一个表达式
    view.setOnLabelCheckedListener { label ->
        println(label)
    }
```

最终的代码和之前的代码有两个最大的不同，一是没有了接口定义，二是没有了匿名内部类。

在使用 kotlin 的时候要时刻保持函数式编程的思想。


