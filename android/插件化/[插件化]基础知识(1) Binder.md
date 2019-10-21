# Binder

Binder(绑定服务) 是客户端-服务器接口中的服务器。绑定服务可让组件（例如 Activity）绑定到服务、发送请求、接收响应，甚至执行进程间通信 (IPC)。Binder 通常只在为其他应用组件服务时处于活动状态，不会无限期在后台运行。 Binder 是一个很复杂的话题，网上关于讲 Binder 的文章也有很多，本篇文章主要是记录我学习 Binder 使用过程中的一些收获，并不深入的讨论 Binder 的底层细节。

## Binder 理解

Binder 是 Android 中的一个类，它实现了 IBinder 接口。

- 从 IPC 角度说，Binder 是Android 中的一种跨进程通信的方式；
- Binder 还可以理解为一种虚拟的物理设备，它的驱动是 /dev/binder ；
- 从Android Framework角度来说，Binder是ServiceManager连接各种Manager（ActivityManager、WindowManager，etc）和相应ManagerService的桥梁；
- 从Android应用层来说，Binder是客户端和服务端进行通信的媒介，当你bindService的时候，服务端会返回一个包含了服务端业务调用的Binder对象，通过这个Binder对象，客户端就可以获取服务端提供的服务或者数据，这里的服务包括普通服务和基于AIDL的服务；

## Binder 的实现

关于 Binder 的实现可以通过以下三种方式：

- 扩展 Binlder 类

    同进程间的最常见的就是绑定 service 时使用 obBind() 返回 Binder 实例，然后通过 onServiceConnected() 回调接受 Binder。
    此方法只有在客户端和服务位于同一应用和进程内这一最常见的情况下方才有效。 

- 使用 Messenger

    通常用于不同进程间的服务与客户端之间的通讯。是实现 IPC 的最简单的方法， Messenger 会在单一线程中创建包含所有请求的队列，因此不必对服务进行线程安全设计。其底层是通过 AIDL 来实现的。

- 使用 AIDL

    AIDL（Android 接口定义语言）执行所有将对象分解成原语的工作，操作系统可以识别这些原语并将它们编组到各进程中，以执行 IPC。

# 通过实现一个 AIDL 来理解 Binder

实现 AIDL 的过程可以分为三步：

- AILD 接口创建

    AIDL 接口即是服务端暴露给客户端的接口，服务端和客户端其实就是通过这些接口来通讯的。

- 服务端

    创建一个 service 用来监听客户端的请求，然后再其中实现定义好的 AIDL 接口即可。

- 客户端

    绑定服务端的 service，将服务端返回的 Binder 对象转换成 AIDL 接口类型，接着调用 AIDL 中的方法就可以了。


