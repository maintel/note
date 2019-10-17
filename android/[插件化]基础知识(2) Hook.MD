
# Hook

hook 又称钩子，通常指对一些方法进行拦截。这样当这些代码方法被调用时，也能够执行我们自己的代码，即面向切面编程的思想(AOP)。

Android 本身不提供这种拦截机制，但是我们可以通过特殊的手段来实现。

大致思路就是：

- 找到要 Hook 的类及方法

- 动态代理来代理系统类的运行并拦截需要拦截的方法

- 使用反射将这个系统类替换成自己的代理类


![](http://blogqn.maintel.cn/%E6%88%91%E7%90%86%E8%A7%A3%E7%9A%84hook%E6%9C%BA%E5%88%B6.png?e=3080650131&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:mJTZljePV685WLpKgFgyLxrojh4=)