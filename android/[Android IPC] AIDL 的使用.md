# AIDL

AIDL(Android Interface Definition Language) 翻译成中文就是 Android 接口定义语言，用于生成 Android 设备上两个进程之间进行通讯的代码。它是 Binder 机制向外提供的接口，它使用代理类在客户端和服务端传递数据。

本篇主要记录 AIDL 学习过程以及一些坑。

# AIDL 的使用

AIDL 的使用主要分为以下三步：

- 创建 .aidl 文件

    即 AIDL 接口，是服务端暴露给客户端的接口，服务端和客户端其实就是通过这些接口来通讯的。

- 服务端

    创建一个 service 用来监听客户端的请求，然后再其中实现定义好的 AIDL 接口即可。

- 客户端

    绑定服务端的 service，将服务端返回的 Binder 对象转换成 AIDL 接口类型，接着调用 AIDL 中的方法就可以了。

## 创建 .aidl 文件

这里有一个 Book 类，服务端与客户端之间传递的主要数据实体就是它了。在创建 .aidl 文件前先建立此类。

```java
package com.maintel.binderdemo1.model;

...

public class Book implements Parcelable {

    private int boolId;
    private String bookName;

    ...//为了节省篇幅这里省略了一些代码，get set 以及 实现 Parcelable 接口的一些代码
}
```

这里为什么要实现 Parcelable 是因为 AIDL 在实现进程间通讯的过程时就是一个对数据序列化和反序列化的过程。

AIDL 文件支持的数据类型如下：

- Java 编程语言中的所有原语类型（如 int、long、char、boolean 等等）
- String 和 CharSequence
- List

    List 中的所有元素都必须是以上列表中支持的数据类型、其他 AIDL 生成的接口或声明的可打包类型。 可选择将 List 用作“通用”类（例如，List<String>）。另一端实际接收的具体类始终是 ArrayList，但生成的方法使用的是 List 接口。

- Map

    Map 中的所有元素都必须是以上列表中支持的数据类型、其他 AIDL 生成的接口或声明的可打包类型。 不支持通用 Map（如 Map<String,Integer> 形式的 Map）。 另一端实际接收的具体类始终是 HashMap，但生成的方法使用的是 Map 接口。

- 实现了 Parcelable 接口的对象

下面就来创建所需的 .aidl 文件

快速创建 aidl 文件可以如下步骤：

![](http://blogqn.maintel.cn/创建aidl1.png?e=3080192722&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:luqc2vxLIk7QCHtY5x0wIBXxUss=)

因为用到了 Book 这个类，所以也要创建 Book.aidl 如下：

```java
// Book.aidl
package com.maintel.binderdemo1.model;

parcelable Book;  //注意这里的 parcelable 和 Parcelable 不一样，前者是一个类型
```

*注意这里`package com.maintel.binderdemo1.model`必须要和 Book 类的包名一致！要不然在自动生成的时候会找不到类*

然后创建接口类 IBookManager.aidl

```java
// IBookManager.aidl
package com.maintel.binderdemo1;

// Declare any non-default types here with import statements
import com.maintel.binderdemo1.model.Book;

interface IBookManager {

    List<Book> getBookList();

    void addBook(in Book book);

}
```

关于上面的代码：

- `import com.maintel.binderdemo1.model.Book;`

    因为下面的方法中用到的 Book, 所以我们需要显式的引入进来，即使有时候两者在同一个包下。

- ` void addBook(in Book book);` 中的 in

    除了基本数据类型外，其他的类型参数必须标上 in、out、inout，in 表示输入型参数，out 表示输出型参数，inout 表示输入输出型参数。

至此接口类就已经完成了，此时 build 一下项目如果使用的是 Android studio 会在 app/build/generated/source/aidl/debug/package name 下看到自动生成的 IBookManager。

## 创建服务端

服务端就很简单了，首先新建一个名为 BookManagerService 的 service：

```java
package com.maintel.binderdemo1.service;

public class BookManagerService extends Service {
    private CopyOnWriteArrayList<Book> mBookList = new CopyOnWriteArrayList<>();

    @Override
    public void onCreate() {
        super.onCreate();
        mBookList.add(new Book(1, "Java"));
        mBookList.add(new Book(2, "JS"));
        mBookList.add(new Book(3, "Android"));
    }   

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return mBinder;
    }

    private Binder mBinder = new IBookManager.Stub() {

        @Override
        public List<Book> getBookList() throws RemoteException {
            return mBookList;
        }

        @Override
        public void addBook(Book book) throws RemoteException {
            mBookList.add(book);
        }
    }; 
}
```
这里使用了 CopyOnWriteArrayList 它不是继承自 ArrayList 的，但是为什么可以使用呢？是因为 AIDL 支持的是抽象的 List 接口，因此虽然服务端返回的是 CopyOnWriteArrayList，但是在 Binder 中还是按照 List 的规范去访问数据，最终形成一个 ArrayList 返回给客户端。

在清单文件中注册，并使其运行在另外的进程中：

```xml
        <service
            android:name=".service.BookManagerService"
            android:process=":remote"/>
```

## 客户端实现

客户端的实现就是一个绑定 service 的过程：

```java
public class MainActivity extends AppCompatActivity {

    private IBookManager bookManager;

    private ServiceConnection mConnection = new ServiceConnection() {
        @Override
        public void onServiceConnected(ComponentName componentName, IBinder iBinder) {
            bookManager = IBookManager.Stub.asInterface(iBinder);

            try {
                bookManager.addBook(new Book(4,"Html")); //这里调用 addBook 添加一本书
                List<Book> list = bookManager.getBookList();
                Log.d("MainActivity", list.toString());
            } catch (RemoteException e) {
                e.printStackTrace();
            }
        }

        @Override
        public void onServiceDisconnected(ComponentName componentName) {
            Log.d("MainActivity.onServiceDisconnected");
            bookManager = null;
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Log.e("MainActivity", "Thread.currentThread():" + Thread.currentThread());
        Intent intent = new Intent(this, BookManagerService.class);
        bindService(intent, mConnection, BIND_AUTO_CREATE);
    }

    @Override
    protected void onDestroy() {
        unbindService(mConnection);
        super.onDestroy();
    }
}
```

此时运行客户端程序打印出 log：

```
D/MainActivity: [Book{boolId=1, bookName='Java'}, Book{boolId=2, bookName='JS'}, Book{boolId=3, bookName='Android'}, Book{boolId=4, bookName='Html'}]
```

至此一次完整的使用 AIDL 进行 IPC 的过程就完成了。

至于其使用过程中的一些注意事项后面再说。

# 关于 AIDL 的理解

我个人关于 AIDL 的一些理解，不知道是否准确

AIDL 是一门语言，它是为了更方便的使用 Binder 而生的。按照规范写一个 .aidl 文件，插件会自动生成同名的 java 文件，而这些 java 文件才是具体实现，为什么要有 AIDL 其实是为了更标准化以及简化 Binder 的使用，让开发者更多的关注与功能的实现上。
