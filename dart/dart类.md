# calss

一些初始特性和 java 类似，下面是一些例子：

```dart
class Test{
  String name;
  num age;
  // 默认有一个无参构造函数
}

class Test2{
  String name;
  num age;
  // 构造参数
  Test2(String name, num age){
    this.name = name;
    this.age = age;
  }
}

class Test3{
  String name;
  num age;
  // 也可以直接这样写
  Test3(this.name, this.age);
}
```

值得注意的是 dart 不能有多个构造函数，当需要多个构造函数的时候需要通过下面的写法：

```dart
class Test3{
  String name;
  num age;

  Test3(this.name, this.age);

  Test3.origin(){
    name = "maintel";
    age = 10;
  }

  Test3.newInstance(String name,int age){
    this.name = name;
    this.age = age;
  }
  
}
```

## 构造函数

### 继承

初始化顺序，

- 初始化列表
- 父类无参构造函数
- 主类无参构造函数

```dart
class Person{
  String firstName;

  Person(){
    print("person constructor");
  }

  Person.fromJson(Map data) {
    print('in Person');
  }
}

class Employee extends Person {
  // 如果父类有一个默认的构造函数，则不需要调用super
  Employee.fromJson(Map data)  {
    print('in Employee');
  }
}
```

因为在调用主类的构造函数之前要先确定父类的构造，所以像例子中的情况 `Employee.fromJson`:

- 在父类没有无惨构造函数的情况下需要调用父类的 `formJson`
- 即使父类已经有了有参构造函数，也是需要调用父类的 `formJson` 函数，因为如果不调用无法初始化。
    这个时候带来一个问题，如果父类只有有参构造函数的时候必须要实现另外一个构造方法，否则子类实现了一个其他构造函数的时候无法初始化，像下面这样：

```dart
class Person{
  String firstName;
  Person(this.firstName);
}

class Employee extends Person {
  Employee(String name):super(name);
  Employee.fromJson(Map data)  {  // 这里会报错，因为无法初始化父类
    print('in Employee');
  }
}
```

- 如果父类为空实现，那么就不需要调用父类的任何方法，当然也无方法可调。

### 初始化成员列表

可以直接通过跟在一个 ： 后面来初始化变量。。。但是感觉和写在构造函数中并无区别。

区别就是在于初始化列表是在构造函数的 `{}` 中的内容执行前执行的。

```dart
  InitializerTest(x,y)
      : x = x,
        y = y,
        sum = x + y {
            // do something
        }
```

### 构造函数重定向

```dart
  // 重定向构造函数
  InitializerTest.newInstance(x) : this(x,10);

  ```

### 常量

如果确定一个类中的数据不会发生变化，可以定义一个常量类，构造函数使用 `const` 来标记。

```dart
class TestCosnt {

  //常量类中的变量必须都是 final 的
  final String data;

  final String name;
  final int age;

  /**
   * 当使用 cosnt 标记一个构造函数是，它类似于java的单例
   * 而且这个时候这个类中的变量都应该是 fianl 的
   */
  const TestCosnt(this.data,{
    this.name = "laowang",
    this.age = 10
  });
}
```

当初始化两个相同的常量类的时候，他们两个是相同的，是同一个对象

```dart
  var testConst = const TestCosnt("testConst");
  var testConst2  = const TestCosnt("testConst 2222");
  var testConst3  = const TestCosnt("testConst");

  print(testConst == testConst2);  // false
  print(testConst == testConst3);  // true
  print(identical(testConst, testConst3)); // true
```

### 工厂构造函数

Dart 中有一个关键字 factory，可以用来替代默认的构造函数，做一些缓存什么的。比如下面这个：

```dart
class Logger {
  final String name;
  bool isDebug = true;

  static final Map<String, Logger> _cache = <String, Logger>{};

  factory Logger(String name){
      if(_cache.containsKey(name)){
        return _cache[name];
      } else {
        final logger = Logger._internal(name);
        _cache[name] = logger;
        return logger;
      }
  }

  void log(String msg){
    if(isDebug) {
      print(msg);
    }
  }

  Logger._internal(this.name);
}

// 调用起来并没有什么不同

Logger("name").log("teaadad");

```

factory 用来替代默认的构造函数，它使用起来和默认构造函数没有区别，但是在函数内部和构造函数是有区别的：

- 它有返回值
- 内部不能使用 this 关键字

### 单例类

可以用上面的 factory 来写单例:

```dart
class SingleClass {

  factory SingleClass() {
    return _getInstance();
  }

  static SingleClass _instance;

  SingleClass._new(){

  }

  static SingleClass _getInstance(){
    if(_instance == null){
      _instance = new SingleClass._new();
    }
    return _instance;
  }

}
```

# 方法

## 抽象方法和抽象类

使用上和 java 并无区别，都是使用 abstract 关键字。

有一个要注意的就是，可以使用 factory 关键字使 抽象类看起来是可以被实例化的：

```dart
abstract class AbstractFactoryClass {
  void test();
  factory AbstractFactoryClass(){
    // 即使这里写了构造方法，直接报错，因为给它 factory 以后也只是看起来能被实例化而已
    // return AbstractFactoryClass._internal();
  }

  AbstractFactoryClass._internal();

  void log(){
    print("this is abstract class");
  }
}

// 调用
  var abstracts = AbstractFactoryClass();

  // abstracts.log(); // 运行报错
```

比如上面的代码，看起来没什么问题，运行的时候就报错了。所以 使用 factory 关键字也只是使抽象来看起来能被实例化一样，实际上并不能被实例化。。。

## 隐式接口

在 dart 中所有的类都可以看做是接口，dart 中没有 interface 关键字。

关于这个的说明可以参考这个博客-[Eliminating Interface Declarations from Dart](https://news.dartlang.org/2012/06/proposal-to-eliminate-interface.html)

大概就是说在 dart 中所有的类都是隐式的接口，而且接口完全可以用纯粹的抽象类来代替