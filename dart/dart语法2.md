# 操作符

一般操作符和 java 以及 kotlin 没有区别，这里关注几个不一样的。

## ... 级联操作符

```dart
  // .. 是级联操作符，有点像 react 中的级联操作符
  // 它和 java 的链式编程是有区别的，它对当前这个对象起作用。比如下面这样
  var test = Test() // 初始化一个对象 test
              ..name = "test" // 设置name 为 test
              ..age = 10  //设置 age 为 10
              ..hello() // 调用了一下 hello 函数
              ..getName() // 调用了一下 getName 函数 
              ..name = "maintel"; // 设置了 name 为 maintel


class Test{
  var name;
  var age = 0;

  void hello(){
    print("name::$name  age::$age");
  }

  String getName(){
    return name;
  }
}
```

## ~/ 整除

```dart
  print("${5 ~/ 2}");  // 2
  print("${5 / 2}");  // 2.5
  print("${5 % 2}");  // 1
```

## ??=  如果为空则赋值

```dart
  var b = 10;
  b ??= 100;
  print(b); // b 不为空，所以不赋值 输出 10
  var c;
  c ??= 100;
  print(c); // c 为空，赋值100 输出 100
```

## ?? 测试是否为空

如果为空则返回 ?? 后面的内容，否则返回自身

```dart
  var boolean;
  print(boolean ?? "test"); // boolean为空所以输出 test
```

## ==

```dart
/**
 * `==` 操作符，其实是一个方法，甚至可以被重写
 * 当使用它的时候其实是调用了`x==y` 其实就是 `x.==(y)`
 */
```

# 控制流

和 kotlin 并区别，`if else`,`for`,`for in`,`while` 等都一样。

不同的是 switch 和 java 类似，不能像 kotlin 那样支持多种类型，在 dart 中 switch 的分支必须是相同类型，哪怕是子类也不行。和 java 不同的是，虽然 case 的条件也需要是一个常量，但是这个常量可以是任意对象。
