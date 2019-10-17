任何一个应用都是由多了为了实现业务目标而相互协作的对象构成，传统的方法中创建这些对象间的关联关系通常通过构造器或者查找，而这通常会导致高度耦合、结构复杂、难以复用以及难以进行单元测试。

在 Spring 中，对象无需自己查找或者创建与其关联的其他对象，容器负责把需要相互协作的对象引用赋予各个对象。创建对象之间的协作关系行为称为**装配**，这也是依赖注入（DI）的本质。

<!--more-->

# Spring 装配 bean

Spring 提供了三种装配机制：

- 在 XML 中进行显式配置；
- 在 Java 中进行显式配置；
- 隐式的 Bean 发现机制和自动装配。

这三种方式可以互相搭配，而且没有说明某个场景下一定要选用哪种机制。

## 自动化装配 Bean

自动化装配是最便利的配置方案。需要从两个角度来实现：

- 组件自动扫描（component scanning）：Spring 会自动发现应用中上下文创建的 bean；
- 自动组装（autowiring）：Spring 自动满足 bean 间的依赖。

（哦 就是 @component 和 @Autowired 嘛）

但是在使用的时候需要显式的配置 Spring，好让其去主动寻找带有 @component 注解的类，并创建 bean。有两种方式指定：

方式一：
```java
@Configuration
@ComponentScan  //启用组件扫描。
public class Config {
}

```
@componentScan 默认会扫描当前包下及所有子包，自动查找带有 @component 注解的类。

方式二：

```xml
<context:component-scan base-pakage="packageName"/>
```
component-scan 和 @ComponentScan 注解有相同的属性，有以下两个重要的属性：

- basePackage 

    指定一个或者多个包名。

- basePackageClasses

    指定扫描的类或者实现了某个接口的类。

**@Autowired** 注解可以实现自动装配，就是在 Spring 在创建一个 bean 的时候，会根据它来实现自动加入此 bean 所需要的依赖。

比如下面：

```java
@Component
public class Engine {

    public void power() {
        System.out.println("go go go!");
    }

}

@Component
public class Car {

    @Autowired   //通过注解自动注入
    Engine engine;

    public void go() {
        engine.power();
    }
}

@Configuration  //表明这是一个配置类
@ComponentScan  //配置扫描
public class Config {
}

// 在一个测试类中进行测试。
public class Test {

    public static void main(String[] args) {
        BeanFactory factory = new AnnotationConfigApplicationContext(Config.class); //解析配置类
        Car car = factory.getBean(Car.class);
        car.go();
    }
}

// 运行Test 类可以看到输出 go go go!
```

@Autowired 注解可以有多种用法，可以用在构造函数中，或者一个方法上。同时可以使用 java 原生的 @Inject 注解来代替它，在大多数情况下是没有任何问题的。

大多数时候使用自动化配置来装配 bean，但是有时候这种方法行不通，比如引用一个第三方库的类时，没法给它添加注解，这个时候就需要用到下面两个方法。

## 通过 Java 装配 bean

通过 Java 来装配 bean 很简单，主要是借助 JavaConfig 来实现注入。有两个注解

- Configuration 声明一个配置类
- @Bean 创建一个 bean 实例

改造上面的例子：

```java
// Engine 和 Car 不带有任何注解的普通 java 类
// 配置类
@Configuration
public class Config {
    @Bean
    public Engine getEngine() {
        return new Engine();
    }

    @Bean
    public Car getCar(){
        return new Car(getEngine()); 
    }

    @Bean
    public Car getCar2(){
        return new Car(getEngine());
    }
}

    // 测试
    public static void main(String[] args) {
        BeanFactory beanFactory = new AnnotationConfigApplicationContext(Config.class);
        Car car = (Car) beanFactory.getBean("getCar");  // 获取方法就是根据方法名，除非显式的指定了 @Bean 的 name 属性
        car.go();
        System.out.println(car.getEngine());
        Car car2 = (Car) beanFactory.getBean("getCar2");
        car2.go();
        System.out.println(car2.getEngine());
    }
// 通过输出可以看到 car 和 car2 中的 engine 对象时同一个。
```
上面方法中写了一个`new Car(getEngine())`,似乎每次执行都会new 一个新的 engine 实例，但事实并非如此，因为如果一个方法带有 @bean 注解，在默认情况下 Spring 会拦截所有对它的调用，并确保返回该方法创建的 bean，而不是每次都对其进行实际调用。另外需要说明的是，可以在带有 @Bean 注解的方法中做任何 Java 允许做的事情。

## 使用 XML 来装配 bean

通过 xml 来配置的方式在 Spring 历史中已经存在了很长时间，同时使用起来也比较复杂。具体使用可以用下面一图来表示。

![](http://blogqn.maintel.cn/TIM截图20170901164502.png?e=3081054847&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:WfKEQPLL18PbQw2U39GNAuz1Yus=)


以上是装配 Bean 的三种方式，这三种方式并不是只能独立的使用，它们之间可以相互混用，从而达到最佳方案。


# 高级装配

上面讲了 Spring 装配 bean 基本方法，Spring 还提供了很多高级的用法。

## 配置 profile bean

最常见的情况是，开发过程中连接数据库在不同阶段使用的链接不同，开发环境，测试环境，生产环境等等。通过 profile 的配置可以灵活的切换他们而不引起问题。例如：

```java
@Configuration
public class Config{

    @Bean
    @Profile("dev") //开发环境
    public DataSource devDataSource(){
        ...
    }

    @Bean
    @Profile("test") //测试环境
    public DataSource testDataSource(){
        ...
    }
}

//同样也可以通过 xml 来配置 <bean profile="dev">...</bean>
```
然后就是如何激活 profile 了，当 profile 处于激活状态时才会创建这个 bean，如果没有都没有处于激活状态的话，则都不会创建。profile 的激活主要依赖于两个属性：
- spring.profiles.active
- spring.profiles.default

这两个属性相互独立，active 用来确定哪个 profile 会被激活，default 确定默认值。Spring 提供了多种方式来配置这两种属性：
- 作为 DispatcherServlet 的初始化参数；
- 作为 Web 应用的上下文参数；
- 作为 JNDI 条目；
- 作为环境变量；
- 作为 JVM 的系统属性；
- 在集成测试类上，使用 @ActiveProlfiles 注解设置。

## 条件化 bean

使用 @Conditional 注解可以约束只有当一个 bean 满足了特定的条件后才能被创建。注意：只有 Spring 4 以后才提供此注解。

```java
    @Bean
    @Conditional(ConditionalTest.class)
    public Car getCar2() {
        return new Car(getEngine());
    }

public class ConditionalTest implements Condition {
    @Override
    public boolean matches(ConditionContext conditionContext, AnnotatedTypeMetadata annotatedTypeMetadata) {
        //something
        return false;
    }
}
```
如上面所示，@Conditional 注解必须给定一个实现了 Condition 接口的类，这个接口的实现很简单，通过 matches 方法返回值来确定是否创建 bean，true 则创建，false 则不创建。matches 方法给定的两个参数能够帮我们做很多事情，例如检查 bean 的定义、检查 bean 是否存在、检查某个资源是否加载、检查类的加载情况、检查是否有其他约束等。

而从 Spring 4开始 @Profile 也是通过 @Conditional 注解来实现的。