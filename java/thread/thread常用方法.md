
值得注意的一点是，多线程的执行结果和 CPU 核心数有关。具体关系好像挺复杂的，有待研究。

# setPriority

设置线程优先级，值为 0-10 越大则优先级越高，默认值为 5。

# sleep

休眠线程，让出 CPU 执行时间，sleep 会一直持有锁对象，即使它已经被休眠。而且在休眠结束后线程不一定会马上执行，而是变成可执行状态。

# yield

让出 CPU 执行给相同优先级的线程，暂停当前正在执行的线程对象，并执行其他线程。
    
yield()应该做的是让当前运行线程回到可运行状态，以允许具有相同优先级的其他线程获得运行机会。因此，使用yield()的目的是让相同优先级的线程之间能适当的轮转执行。但是，实际中无法保证yield()达到让步目的，因为让步的线程还有可能被线程调度程序再次选中。

## sleep()和yield()的区别

sleep()使当前线程进入停滞状态，所以执行sleep()的线程在指定的时间内肯定不会被执行；yield()只是使当前线程重新回到可执行状态，所以执行yield()的线程有可能在进入到可执行状态后马上又被执行。

sleep 方法使当前运行中的线程睡眼一段时间，进入不可运行状态，这段时间的长短是由程序设定的，yield 方法使当前线程让出 CPU 占有权，但让出的时间是不可设定的。实际上，yield()方法对应了如下操作：先检测当前是否有相同优先级的线程处于同可运行状态，如有，则把 CPU  的占有权交给此线程，否则，继续运行原来的线程。所以yield()方法称为“退让”，它把运行机会让给了同等优先级的其他线程
    
另外，sleep 方法允许较低优先级的线程获得运行机会，但 yield()  方法执行时，当前线程仍处在可运行状态，所以，不可能让出较低优先级的线程些时获得 CPU 占有权。在一个运行系统中，如果较高优先级的线程没有调用 sleep 方法，又没有受到 I\O 阻塞，那么，较低优先级线程只能等待所有较高优先级的线程运行结束，才有机会运行。 

# interrupt

给线程发送一个中断信号，让线程在无限循环或者阻塞等的时候抛出一个异常`InterruptedException`从而结束线程，如果在线程内部自己处理了这个异常的话，线程还是不会被结束掉的。

# join

等待线程终止，join是Thread类的一个方法，启动线程后直接调用，即join()的作用是：“等待该线程终止”，这里需要理解的就是该线程是指的主线程等待子线程的终止。也就是在子线程调用了join()方法后面的代码，只有等到子线程结束了才能执行。比如一个线程需要另外一个线程的计算结果或者什么时，可以使用此函数。

**举个例子**

有两个线程 JoinA 和 JoinB，两个线程同时启动，JoinA 需要依赖于 JoinB 的计算结果，但是 JoinB 比较耗时。

JoinA 线程：

```java
public class JoinA implements Runnable {

    private int sum;
    private JoinB joinB;
    private Thread thread;

    JoinA() {
        joinB = new JoinB();
        thread = new Thread(joinB);
        thread.start();
    }

    @Override
    public void run() {
        for (int i = 0; i < 5; i++) {
            sum += i;
            System.out.println("JoinA sum::" + sum);
            if (i == 2) { // 模拟需要计算结果
                // 这里加入了 join 意思是 JoinTest2 必须要等到 joinTest 线程执行完毕才会继续执行。
                try {
                    thread.join();
                } catch (InterruptedException e) {
                }
                // 这里等待 joinTest 的计算结果，然后加入到里面来
                sum = sum + joinB.getSum();
            }
            try {
                Thread.sleep(800);
            } catch (InterruptedException e) {
            }
        }
    }
}
```

JoinB 线程:

```java
public class JoinB implements Runnable {

    private int sum;

    public int getSum() {
        return sum;
    }

    @Override
    public void run() {
        for (int i = 0; i < 5; i++) {
            sum += i;
            System.out.println("JoinB sum::" + sum);
            try {
                // 这里不能使用 wait 因为没有锁
//                wait(1000);
                Thread.sleep(1000);
            } catch (InterruptedException e) {
            }
        }
    }
}
```

调用 `new Thread(new JoinA()).start();` 结果：

> JoinB sum::0
> JoinA sum::0
> JoinA sum::1
> JoinB sum::1
> JoinA sum::3
> JoinB sum::3
> JoinB sum::6
> JoinB sum::10
> JoinA sum::16
> JoinA sum::20

可以看到 A 线程等待 B 线程执行完得到计算结果后才继续向下执行。

如果不加 join 方法，结果：

> JoinB sum::0
> JoinA sum::0
> JoinA sum::1
> JoinB sum::1
> JoinA sum::3
> JoinB sum::3
> JoinA sum::7
> JoinB sum::6
> JoinA sum::11
> JoinB sum::10

# wait

wait 是 object 的方法，它必须和 notify 以及 synchronized 一起使用，否则会抛出异常。作用是在获取锁对象后，主动释放锁同时线程休眠，直到其他线程使用 notify 唤醒，或者休眠时间到。但有一点需要注意的是notify()调用后，并不是马上就释放对象锁的，而是在相应的synchronized(){}语句块执行结束，自动释放锁后，JVM会在wait()对象锁的线程中随机选取一线程，赋予其对象锁，唤醒线程，继续执行。这样就提供了在线程间同步、唤醒的操作。Thread.sleep()与Object.wait()二者都可以暂停当前线程，释放CPU控制权，主要的区别在于Object.wait()在释放CPU同时，释放了对象锁的控制。

例子：

建立三个线程，A线程打印10次A，B线程打印10次B,C线程打印10次C，要求线程同时运行，交替打印10次ABC。

 ```java
public class WaitABCTest implements Runnable {

    private String name;
    private Object last;

    WaitABCTest(String name) {
        this.name = name;
    }

    public void setLast(Object last) {
        this.last = last;
    }

    @Override
    public void run() {
        for (int i = 0; i < 10; i++) {
            synchronized (last) {
                synchronized (this) {
                        System.out.println(name);
                        this.notify();
                }
                try {
                    last.wait();
                } catch (Exception e) {
                    System.out.println(e);
                }
            }
        }
    }
}
 ```

 调用：

 ```java
    private static void waitAbc() {
        WaitABCTest abcTestA = new WaitABCTest("A");
        WaitABCTest abcTestB = new WaitABCTest("B");
        WaitABCTest abcTestC = new WaitABCTest("C");
        abcTestA.setLast(abcTestC);
        abcTestB.setLast(abcTestA);
        abcTestC.setLast(abcTestB);
        new Thread(abcTestA).start();
        Thread.sleep(10);
        new Thread(abcTestB).start();
        Thread.sleep(10);
        new Thread(abcTestC).start();
    }
 ```