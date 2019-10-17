<!-- TOC -->

- [问题重现](#问题重现)
- [错误代码](#错误代码)
- [解决办法](#解决办法)
- [原因](#原因)

<!-- /TOC -->

# 问题重现

> Failed adding to JNI pinned array ref table (1024 entries)

在开发蓝牙模块升级的时候， 由于要传送的升级文件较大，而 BLE 模块一次传输数据大小有限制，因此需要拆包，并需要频繁的通过JNI调用so库来组装报文，结果在低版本手机测试时遇到`Failed adding to JNI pinned array ref table (1024 entries).`

# 错误代码

下面是出现错误的函数：
```c
JNIEXPORT jbyteArray JNICALL xxx_BleUtils_sendUpdatePkt(
        JNIEnv *env, jclass jobj, jbyteArray pkt, jint pkt_sn, jint pktLen, jint token
) {
    unsigned long outbuf[APPAPI_MAXSENDLEN / 4];
    unsigned char *pBuffer = (*env)->GetByteArrayElements(env, pkt, NULL);   //<==引起错误的地方
    int ret = ynLockSendPkt((uint16_t) token, (uint16_t) pkt_sn, pktLen,
                            pBuffer,
                            (char *) outbuf,
                            APPAPI_MAXSENDLEN);
    jbyteArray array = (*env)->NewByteArray(env, ret);
    (*env)->SetByteArrayRegion(env, array, 0, ret, outbuf);
    return array;
}
```

# 解决办法

查询官方文档也可以知道需要通过 `ReleaseByteArrayElements`来及时的释放资源：

```c
(*env)->ReleaseByteArrayElements(env,pkt, pBuffer, 0); //pkt为java层传递过来的数组，pBuffer为指针
```

# 原因

其实 GetByteArrayElements 就类似于一个 new 的操作，而在 new 以后没有进行释放，而 C 并不会自动的去回收这些内容，所以频繁调用的情况下，引用次数不断增加，最终导致溢出。

后来查阅资料发现，上面的说法并不准确，首先 GetByteArrayElements 会创造出一个局部引用，JNI 会将创建的局部引用都存储在一个局部引用表中，如果这个表超过了最大容量限制，就会造成局部引用表溢出（比如本例中的 1024，在配置更低的手机中这个值可能更小），使程序崩溃。但是关于局部引用的释放问题，除了我们可以手动进行释放以外，**函数被调用完成后，JVM 会自动释放函数中创建的所有局部引用**。

那么在上面的错误代码中，很显然方法执行结束后会自动释放 GetByteArrayElements 所创建的局部引用，而实验证明确实是这样：

java 测试代码：
```java
    byte[] b = {0x00};

    public void test() {
        for (int i = 0; i < 20000; i++) {
            System.out.println("aaaaaa::" + i);
            EAJniUtils.test2(b);
        }
    }
```
JNI 代码：
```c
JNIEXPORT jint JNICALL xxx_utils_EAJniUtils_test2
  (JNIEnv *env, jclass jobj, jbyteArray pkt){
    unsigned char *pBuffer = (*env)->GetByteArrayElements(env, pkt, NULL);
    return 0;
  }
```
可以看到上面 test2 函数没有释放局部变量，而在 java 层对他进行了 20000 此循环调用，程序没有崩溃。

因此正确的原因应该是在原始代码的`ynLockSendPkt`函数中某个地方持有了 pBuffer 指针，导致它一直不被释放，所以我们后面手动的对它进行了释放。然而事实上问题到这里并没有完全被解决，因为是引入的第三方so所以也没办法看到具体原因，但是至少知道了问题出在什么地方。