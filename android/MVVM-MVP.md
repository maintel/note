# MVC

**View：**XML布局文件。 **Model：**实体模型（数据的获取、存储、数据状态变化）。 **Controller：**对应于Activity，处理数据、业务和UI。

Android本身的设计还是符合MVC架构的，但是Android中纯粹作为View的XML视图功能太弱，我们大量处理View的逻辑只能写在Activity中，这样Activity就充当了View和Controller两个角色，直接导致Activity中的代码大爆炸.

# MVP

**View:**对应于Activity和XML，负责View的绘制以及与用户的交互。 **Model:**依然是实体模型。 **Presenter:**负责完成View与Model间的交互和业务逻辑。

Activity充当了View和Controller两个角色，MVP就能很好地解决这个问题，其核心理念是通过一个抽象的View接口（不是真正的View层）将Presenter与真正的View层进行解耦。Persenter持有该View接口，对该接口进行操作，而不是直接操作View层。这样就可以把视图操作和业务逻辑解耦，从而让Activity成为真正的View层。

但MVP也存在一些弊端：

- Presenter（以下简称P）层与View（以下简称V）层是通过接口进行交互的，接口粒度不好控制。粒度太小，就会存在大量接口的情况，使代码太过碎版化；粒度太大，解耦效果不好。同时对于UI的输入和数据的变化，需要手动调用V层或者P层相关的接口，相对来说缺乏自动性、监听性。如果数据的变化能自动响应到UI、UI的输入能自动更新到数据，那该多好！
- MVP是以UI为驱动的模型，更新UI都需要保证能获取到控件的引用，同时更新UI的时候要考虑当前是否是UI线程，也要考虑Activity的生命周期（是否已经销毁等）。
- MVP是以UI和事件为驱动的传统模型，数据都是被动地通过UI控件做展示，但是由于数据的时变性，我们更希望数据能转被动为主动，希望数据能更有活性，由数据来驱动UI。
- V层与P层还是有一定的耦合度。一旦V层某个UI元素更改，那么对应的接口就必须得改，数据如何映射到UI上、事件监听接口这些都需要转变，牵一发而动全身。如果这一层也能解耦就更好了。
- 复杂的业务同时也可能会导致P层太大，代码臃肿的问题依然不能解决。


# MVVM

**View:**对应于Activity和XML，负责View的绘制以及与用户交互。 **Model:**实体模型。 **ViewModel:**负责完成View与Model间的交互，负责业务逻辑。



[美团-如何构建Android MVVM 应用框架](https://tech.meituan.com/2016/11/11/android-mvvm.html)