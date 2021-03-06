
<!-- TOC -->

- [JVM虚拟机的内存模型](#jvm虚拟机的内存模型)
  - [程序计数器](#程序计数器)
  - [java 栈](#java-栈)
  - [本地方法栈](#本地方法栈)
  - [堆](#堆)
  - [方法区](#方法区)
- [哪些情况下的对象会被垃圾回收机制处理掉？](#哪些情况下的对象会被垃圾回收机制处理掉)
- [常见编码方式](#常见编码方式)
- [utf-8编码中的中文占几个字节；int型几个字节](#utf-8编码中的中文占几个字节int型几个字节)
- [静态代理和动态代理的区别，什么场景使用](#静态代理和动态代理的区别什么场景使用)
- [Java的异常体系](#java的异常体系)
- [谈谈你对解析与分派的认识](#谈谈你对解析与分派的认识)
- [修改对象A的equals方法的签名，那么使用HashMap存放这个对象实例的时候，会调用哪个equals方法](#修改对象a的equals方法的签名那么使用hashmap存放这个对象实例的时候会调用哪个equals方法)
- [Java中实现多态的机制是什么](#java中实现多态的机制是什么)
- [如何将一个Java对象序列化到文件里](#如何将一个java对象序列化到文件里)
- [说说你对Java反射的理解](#说说你对java反射的理解)
- [说说你对Java注解的理解](#说说你对java注解的理解)
- [说说你对依赖注入的理解](#说说你对依赖注入的理解)
- [说一下泛型原理，并举例说明](#说一下泛型原理并举例说明)
- [Java中String的了解](#java中string的了解)
- [String为什么要设计成不可变的](#string为什么要设计成不可变的)
- [Object类的equal和hashCode方法重写，为什么](#object类的equal和hashcode方法重写为什么)

<!-- /TOC -->

# JVM虚拟机的内存模型

[参考](https://blog.csdn.net/hxpjava1/article/details/55189077)

JVM 包括

- 类加载器
- 执行引擎
- 运行时数据区

常说的 JVM 内存就是——运行时数据区它包括：

- 程序计数器
- java 栈
- 本地方法栈
- 堆
- 方法区

## 程序计数器

它保存的是程序当前执行的指令的地址（也可以说保存下一条指令的所在存储单元的地址），当CPU需要执行指令时，需要从程序计数器中得到当前需要执行的指令所在存储单元的地址，然后根据得到的地址获取到指令，在得到指令之后，程序计数器便自动加1或者根据转移指针得到下一条指令的地址，如此循环，直至执行完所有的指令。

每个线程都有自己独立的程序计数器，互不干扰。

## java 栈

Java栈是Java方法执行的内存模型。通过它就可以知道java的一个方法的调用过程。

java 栈中存放着一个一个的`栈帧`，每个栈帧对应的就是一个方法，栈帧中包括以下内容：

- 局部变量表

  就是用来存储方法中的局部变量（包括在方法中声明的非静态变量以及函数形参）对于基本数据类型的变量，则直接存储它的值，对于引用类型的变量，则存的是指向对象的引用。
- 操作数栈

  程序中的所有计算过程（其实就是一个方法的具体执行过程）都是在借助于操作数栈来完成的。
- 指向当前方法所属的类的运行时常量池的引用

  在方法执行的过程中有可能需要用到类中的常量，所以必须要有一个引用指向运行时常量
- 方法返回地址

  当一个方法执行完毕之后，要返回之前调用它的地方，因此在栈帧中必须保存一个方法返回地址
- 一些额外的附加信息

每个线程都有一个自己的java栈，互不干扰。

## 本地方法栈

本地方法栈与Java栈的作用和原理非常相似。区别只不过是Java栈是为执行Java方法服务的，而本地方法栈则是为执行本地方法（Native Method）服务的。

## 堆

Java中的堆是用来存储对象本身的以及数组（当然，数组引用是存放在Java栈中的）。只不过和C语言中的不同，在Java中，程序员基本不用去关心空间释放的问题，Java的垃圾回收机制会自动进行处理。因此这部分空间也是Java垃圾收集器管理的主要区域。另外，堆是被所有线程共享的，在JVM中只有一个堆。

## 方法区

它与堆一样，是被线程共享的区域。在方法区中，存储了每个类的信息（包括类的名称、方法信息、字段信息）、静态变量、常量以及编译器编译后的代码等。运行时常量池也在方法区中。


# 哪些情况下的对象会被垃圾回收机制处理掉？

实际回收的时机由 JVM 来确定的或者是手动调用 system.gc 的时候。根据不同的算法回收的时机也不一样。

垃圾回收算法有
- 引用计数法

  引用计数算法，就是标记当前对象被引用的次数，每被引用一次就 +1，当引用超过生命周期或者被设置新值时就 -1，当计数器为0时就回收。这种算法的好处是执行以及回收很及时。缺点是无法检测出循环引用。

- tracing算法(Tracing Collector) 或 标记-清除算法(mark and sweep)

  根搜索算法，程序把所有的引用关系看作一张图，从一个节点GC ROOT开始，寻找对应的引用节点，找到这个节点以后，继续寻找这个节点的引用节点，当所有的引用节点寻找完毕之后，剩余的节点则被认为是没有被引用到的节点，即无用的节点。

  在扫描过程中对存活的对象进行标记，标记完毕后，再扫描整个空间中未被标记的对象，进行回收，如上图所示。标记-清除算法不需要进行对象的移动，并且仅对不存活的对象进行处理，在存活对象比较多的情况下极为高效，但由于标记-清除算法直接回收不存活的对象，因此会造成内存碎片。

- compacting算法 或 标记-整理算法

  标记-整理算法采用标记-清除算法一样的方式进行对象的标记，但在清除时不同，在回收不存活的对象占用的空间后，会将所有的存活对象往左端空闲空间移动，并更新对应的指针。标记-整理算法是在标记-清除算法的基础上，又进行了对象的移动，因此成本更高，但是却解决了内存碎片的问题。在基于Compacting算法的收集器的实现中，一般增加句柄和句柄表。

- copying算法(Compacting Collector)

  该算法的提出是为了克服句柄的开销和解决堆碎片的垃圾回收。它开始时把堆分成 一个对象 面和多个空闲面， 程序从对象面为对象分配空间，当对象满了，基于copying算法的垃圾 收集就从根集中扫描活动对象，并将每个 活动对象复制到空闲面(使得活动对象所占的内存之间没有空闲洞)，这样空闲面变成了对象面，原来的对象面变成了空闲面，程序会在新的对象面中分配内存。一种典型的基于coping算法的垃圾回收是stop-and-copy算法，它将堆分成对象面和空闲区域面，在对象面与空闲区域面的切换过程中，程序暂停执行。

- generation算法(Generational Collector)

  分代的垃圾回收策略，是基于这样一个事实：不同的对象的生命周期是不一样的。因此，不同生命周期的对象可以采取不同的回收算法，以便提高回收效率。

  - 年轻代

    年轻代的目标就是尽可能快速的收集掉那些生命周期短的对象。
    新生代内存按照8:1:1的比例分为一个eden区和两个survivor(survivor0,survivor1)区。一个Eden区，两个 Survivor区(一般而言)。大部分对象在Eden区中生成。一些比较大的对象会生成到老年代中。
    新生代发生的GC也叫做Minor GC，MinorGC发生频率比较高(不一定等Eden区满了才触发)

  - 老年代

    在年轻代中经历了N次垃圾回收后仍然存活的对象，就会被放到年老代中。当老年代内存满时触发Major GC即Full GC，Full GC发生频率比较低，老年代对象存活时间比较长，存活率标记高。
    
  - 持久代

    用于存放静态文件，如Java类、方法等。

GC触发的机制：

  - Scavenge GC（Minor GC）

    一般情况下，当新对象生成，并且在Eden申请空间失败时，就会触发Scavenge GC，对Eden区域进行GC，清除非存活对象，并且把尚且存活的对象移动到Survivor区。然后整理Survivor的两个区。这种方式的GC是对年轻代的Eden区进行，不会影响到年老代。因为大部分对象都是从Eden区开始的，同时Eden区不会分配的很大，所以Eden区的GC会频繁进行。因而，一般在这里需要使用速度快、效率高的算法，使Eden去能尽快空闲出来。

  - Full GC

    对整个堆进行整理，包括Young、Tenured和Perm。Full GC因为需要对整个堆进行回收，所以比Scavenge GC要慢，因此应该尽可能减少Full GC的次数。在对JVM调优的过程中，很大一部分工作就是对于FullGC的调节。有如下原因可能导致Full GC：

    - 年老代（Tenured）被写满
    - 持久代（Perm）被写满 
    - System.gc()被显示调用 
    - 上一次GC之后Heap的各域分配策略动态变化

[参考](http://www.cnblogs.com/sunniest/p/4575144.html)
[参考](https://www.zhihu.com/question/35164211)
[参考](http://icyfenix.iteye.com/blog/715301)

# 常见编码方式

GBK 
ISO-8859-1
UTF-8 一个汉字占用3个字节
UTF-16

# utf-8编码中的中文占几个字节；int型几个字节

中文3个字节，超大字符集里面的汉字站4个字节，英文一个字节，数字字符 1个，int 4个字节

# 静态代理和动态代理的区别，什么场景使用

代理：给某个对象提供一个代理，并由代理对象控制对象对原对象的引用。

- 静态代理

  是由程序员编写的代理类，并在程序运行前就编译好了，而不是由程序动态产生代理类，这就是静态代理。代理关系在程序运行前就已经确定好的。

  设计模式中的代理模式、装饰器模式。

- 动态代理

  动态代理的实现关键技术是——反射。

  动态代理在程序运行时由 java 反射生成，无需手动实现源代码，可以生成任意类型的动态代理类，提高了软件系统的可扩展性。

  使用场景，比如 retrofit 的 create 方法，就使用了动态代理来统一的处理各个接口。AOP 编程的时候，热修复等。


# Java的异常体系

throwable --> error
          --> Exception --> 运行时异常
                        --> 非运行时异常

- error

  一般是程序无法处理的错误，比如 OOM，ANR 等发生时一般会终止程序。

- 运行时异常

  时程序运行时出现的可以处理的错误，比如空指针等。用try catch finally 来捕获异常并处理

- 非运行时异常
  
  编译期就能发现的异常，如果不处理一般编译不能通过。

# 谈谈你对解析与分派的认识

调用目标在编译器进行编译时就必须确定下来，这类方法的调用称为解析

解析调用一定是个静态过程，在编译期间就完全确定，在类加载的解析阶段就会把涉及的符号引用转化为可确定的直接引用，不会延迟到运行期再去完成。而分派调用则可能是静态的也可能是动态的，根据分派依据的宗量数（方法的调用者和方法的参数统称为方法的宗量）又可分为单分派和多分派。两类分派方式两两组合便构成了静态单分派、静态多分派、动态单分派、动态多分派四种分派情况。

- 静态分派

  所有依赖静态类型来定位方法执行版本的分派动作，都称为静态分派，静态分派的最典型应用就是多态性中的方法重载（方法相同，参数不同）。静态分派发生在编译阶段，因此确定静态分配的动作实际上不是由虚拟机来执行的。

- 动态分派

  动态分派与多态性的另一个重要体现——方法覆写（完全相同方法）有着很紧密的关系。向上转型后调用子类覆写的方法便是一个很好地说明动态分派的例子。这种情况很常见，因此这里不再用示例程序进行分析。很显然，在判断执行父类中的方法还是子类中覆盖的方法时，如果用静态类型来判断，那么无论怎么进行向上转型，都只会调用父类中的方法，但实际情况是，根据对父类实例化的子类的不同，调用的是不同子类中覆写的方法。 很明显，这里是要根据变量的实际类型来分派方法的执行版本的。而实际类型的确定需要在程序运行时才能确定下来，这种在运行期根据实际类型确定方法执行版本的分派过程称为动态分派。

# 修改对象A的equals方法的签名，那么使用HashMap存放这个对象实例的时候，会调用哪个equals方法

修改了方法签名后会调用原 equals 方法

```java
if (p.hash == hash &&((k = p.key) == key || (key != null && key.equals(k)))){

}
```

# Java中实现多态的机制是什么

继承、重写、向上转型。

实现方式：接口和继承

通过继承和重写以及父类引用指向子类对象，在调用的时候通过动态绑定来确定引用对象的最终类型，以确定调用的方法。

# 如何将一个Java对象序列化到文件里

通过实现 Serializable、Parcelable(仅限于android) 或者 Externalizable 接口，通过操作文件流的方式以及ObjectOutputStream.writeObject()来写入。

# 说说你对Java反射的理解

当我们的程序在运行时，需要动态的加载一些类这些类可能之前用不到所以不用加载到jvm，而是在运行时根据需要才加载，或者动态的去访问一些类的私有属性或者方法。

反射可以是系统更灵活和易于扩展。比如 spring 的配置这些都是反射来做的。mybatis 也是

使用场景：

- 需要访问隐藏属性或者调用方法改变程序原来的逻辑，这个在开发中是很常见的，由于一些原因，系统并没有开放一些接口出来，这个时候利用反射是一个有效的解决办法。
- 自定义注解，注解就是在运行时利用反射机制来获取的。
- 在开发中动态加载类，比如在 Android 中的动态加载解决65k问题等等，模块化和插件化都离不开反射。

[参考](http://www.sczyh30.com/posts/Java/java-reflection-1/#%E4%B8%80%E3%80%81%E5%9B%9E%E9%A1%BE%EF%BC%9A%E4%BB%80%E4%B9%88%E6%98%AF%E5%8F%8D%E5%B0%84%EF%BC%9F)

# 说说你对Java注解的理解

注解本身不能对代码运行产生影响，但是注解可以作为一个标记，用反射之类的手段获取到这个标记后，就能对标记的内容进行处理。例如在方法参数上加注解，用反射获取到注解后对该注解标记的形式参数注入实际参数。

注解在 java 和 android 中的应用有很多，比如 java 中的 spring，android 中的 butterKnife，Dagger，retrofit 等。

[参考](https://blog.csdn.net/javazejian/article/details/71860633)

# 说说你对依赖注入的理解

说道依赖注入就不得不提控制反转，他们是同一个概念从不同的角度来理解：

- 控制反转（IOC）

  就是创建对象的控制权进行转移，以前创建对象的主动权和创建时机是由自己把控的，而现在这种权力转移到第三方。

- 依赖注入 (DI)

  就是将当前类所依赖的对象通过注入的方式得到，而不再自己去实例化这个对象。

依赖注入的方式有很多：通过构造函数，通过 setter 方法，通过接口等。

例子：
```java
class A{
  B b;      // 这里 b 就是 A 的依赖
  public A(){
    b = new B();   //  现在没有进行依赖注入如果B 的构造方法经常进行变动，则A类也同样需要不断的修改
  }
}
```
上面的就是传统的方法，下面的写法就实现了简单的依赖注入：

```java
class A{
  B b;
  public A(B b){ // 通过构造函数进行依赖注入
    this.b = b;
  }
}
```

上面这段代码就是进行了简单的依赖注入，同时也是控制反转，因为 A 类不在关心它所依赖的 b 实例化的时机在哪里，只要在我 A 类进行实例化的时候通过构造函数给我就行了，同时也不再关心怎么进行实例化，无论B 类如何变动 对A 类都没有影响。这就是控制反转和依赖注入的好处。

能够是系统更灵活，代码的复用率也更高。

比如 spring 控制反转的思想就贯穿始终。还有 android 的 Dagger

[参考](http://luanxiyuan.iteye.com/blog/2279954)
[参考](https://blog.csdn.net/briblue/article/details/75578459)

# 说一下泛型原理，并举例说明

泛型的实现原理是类型擦除，
```java
        List<String> arrayList1=new ArrayList<String>();
        arrayList1.add("abc");
        ArrayList<Integer> arrayList2=new ArrayList<Integer>();
        arrayList2.add(123);
        System.out.println(arrayList1.getClass()==arrayList2.getClass()); // 返回为 true
```

[参考](https://blog.csdn.net/wisgood/article/details/11762427)
[参考](https://blog.csdn.net/shinecjj/article/details/52075499)

# Java中String的了解

String 不可被继承

new string 结果指向堆内存
string = “aaa” 是指向一个常量池，String 是值不可变的，每次更改 String 对象的值都会生成新的对象。

# String为什么要设计成不可变的

节省内存，提高效率，以及安全性
[参考](https://www.zhihu.com/question/31345592)

# Object类的equal和hashCode方法重写，为什么

重写 hashCode 的时候就要重写 equal 在使用散列表类的时候保证了可用性，以避免不必要的错误，
还有就是提高效率，比如将一个自定义的实体类作为 hashMap 的 key 的时候就最好重写 equal 和 hashCode
