> 由于项目中需要接入一下简单的二维码扫描功能，最终使用 zxing 来实现，把官方例子中的部分代码摘除出来做了简单的封装，并进行了一些优化。这里简单做一个记录。

# 扫描二维码

Android 中关于二维码扫描的库有很多，但是归根到底无外乎下面这几种实现方案：

- [zxing](https://github.com/zxing/zxing)
- [ZBar](https://github.com/ZBar/ZBar)

其中基于以上两者实现的比较知名的库有：

- [QRCodeReaderView](https://github.com/dlazaro66/QRCodeReaderView)
- [BGAQRCode-Android](https://github.com/bingoogolapple/BGAQRCode-Android)

后面这两个开源库做的都挺好，可定制化也挺高。不过什么事情都要根据需求来定，就目前的需求而言用不到这么复杂的功能，所以就自己来对官方的项目做一些改造。

# 集成 zxing

因为之前做二维码扫描都是直接集成别人做好的开源方案，也没有看过官方的项目，所以第一眼看到 zxing 官方的项目是懵逼的，不知道从哪下手。不过官方很人性化的写了wiki——[Getting Started Developing](https://github.com/zxing/zxing/wiki/Getting-Started-Developing)，仔细阅读以下也挺简单，在 Android 中使用主要有以下两步：

- 将需要的东西（例如 core）编译成 jar 包或者直接从 [maven](https://repo1.maven.org/maven2/com/google/zxing/) 中下载
- 编译 android 这个模块

不过官方文档中使用的是 mvn 命令，由于没有使用过 mvn，所以也不用按照官方的文档来做了，不过步骤大同小异。

- **方法一** 

首先 clone 下需要的模块：

![](http://blogqn.maintel.cn/TIM%E6%88%AA%E5%9B%BE20180729214642.png?e=3109672239&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:us_3JVxi9Ho83V3cKfbRM1bHa8M=)

然后将 core 编译成 jar 包，将 android 作为工程或者module导入到 Android stuido 中，然后引入 jar 包就可以了。

- **方法二**

这里还有一个更省力的办法，只 clone android 模块，然后作为工程或者 modlue 导入到 Android stuido 中，然后再 gradle 中添加 zxing 的依赖就行了

> compile group: 'com.google.zxing', name: 'core', version: '3.3.2'

这个运行会提示缺少 `CameraConfigurationUtils` 类，这个类在 android-core 这个模块中，我的做法是直接把这个类拷贝到工程中。

然后运行项目即可，运行成功以后是一个 Android 二维码扫描器，[apk 下载](https://play.google.com/store/apps/details?id=com.google.zxing.client.android)。

# 优化

官方的 demo 中功能挺多，打开http、分享、生成二维码等等。不过项目中用不了这么多功能。梳理一下官方的代码：

- CaptureActivity 扫描二维码的 activity；
- ViewfinderView 扫描框 view；
- CameraManager 相机管理；
- OpenCameraInterface 打开相机的具体操作类；
- CaptureActivityHandler 是 CaptureActivity 类中使用的 handler，主要通过他来完成消息传递；
- DecodeThread 图片解码线程；

其他的因为没有使用到暂时没有去管。然后根据需要把一些不必要的代码和逻辑删除剩下的就是一些优化工作。

在使用中主要对他做了两个地方的优化：

- 增加了权限检查
- 把相机的关闭和打开放在了子线程中

## 把相机的关闭和打开放在子线程中

因为相机的打开和关闭是耗时操作，会造成主线程阻塞，然后打开页面卡顿，参考支付宝和微信在打开的时候有一个短暂的加载框，所以这里把相机的打开关闭放在了子线程中来做。主要代码有下面这这些：

### 打开相机

```java
public final class OpenCameraInterface extends Thread {

    private static final String TAG = OpenCameraInterface.class.getName();

    private OpenCamera openCamera;

    private CaptureActivityHandler handler;
    // handler 用来和主线程通讯
    public void setHandler(CaptureActivityHandler handler) {
        this.handler = handler;
    }
    // 由于 camera 对象不能通过 handler 来传递，所以放在这里通过 get 的方式来获取。
    public OpenCamera getOpenCamera() {
        return openCamera;
    }

    private OpenCamera open() {
        int numCameras = Camera.getNumberOfCameras();
        if (numCameras == 0) {
            Log.w(TAG, "No cameras!");
            return null;
        }

        int cameraId = 0;
        while (cameraId < numCameras) {
            Camera.CameraInfo cameraInfo = new Camera.CameraInfo();
            Camera.getCameraInfo(cameraId, cameraInfo);
            if (CameraFacing.values()[cameraInfo.facing] == CameraFacing.BACK) {
                break;
            }
            cameraId++;
        }
        if (cameraId == numCameras) {
            Log.i(TAG, "No camera facing " + CameraFacing.BACK + "; returning camera #0");
            cameraId = 0;
        }

        Log.i(TAG, "Opening camera #" + cameraId);
        Camera.CameraInfo cameraInfo = new Camera.CameraInfo();
        Camera.getCameraInfo(cameraId, cameraInfo);
        Camera camera = Camera.open(cameraId);
        if (camera == null) {
            return null;
        }
        return new OpenCamera(cameraId,
                camera,
                CameraFacing.values()[cameraInfo.facing],
                cameraInfo.orientation);
    }

    @Override
    public void run() {
        try {
            openCamera = open();
        } catch (Exception e) {
            openCamera = null;
        }
        handler.sendEmptyMessage(R.id.open_camera_complete);
    }
}
```
在 CameraManager 中增加一个方法。
```java
    public void openCamera(CaptureActivityHandler handler) {
        // 这里把打开相机放在子线程中
        if (camera != null) {
            return;
        }
        threadOpen = new OpenCameraInterface();
        threadOpen.setHandler(handler);
        threadOpen.start();
    }
```

在 CaptureActivity 中增加一个方法在接到子线程发来的消息后再初始化预览等。这里通过标志位来判断是直接进行初始化还是等待 SurfaceView 创建完成以后再进行初始化。

```java
    public void openCameraComplete() {
        // 如果已有 SurfaceView 就可以继续创建 否则就等待SurfaceView 创建完以后自动执行
        isCameraComplete = true;

        if (hasSurface) {
            SurfaceView surfaceView = (SurfaceView) findViewById(R.id.preview_view);
            SurfaceHolder surfaceHolder = surfaceView.getHolder();
            initCamera(surfaceHolder);
        }
    }
```


### 关闭相机

在关闭相机的时候需要增加必要的线程同步，否则可能造成相机未被关闭。

```java
    public synchronized void closeDriver() {
        // 结束也是耗时操作 方在子线程中
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    // 为了防止在快速切换时出现问题，这里等待打开操作完成后再结束
                    threadOpen.join();
                    if (camera == null) {
                        camera = threadOpen.getOpenCamera();
                    }
                } catch (InterruptedException e) {
                    Log.e(TAG, e.toString());
                }
                camera.getCamera().release();
                camera = null;
            }
        }).start();
    }
```

然后就是权限检查这一块了，没什么好说的在打开相机之前做必要的权限检查就行了。需要注意的是根据官方文档，在 activity onPause 的时候需要关闭相机，然后在 onResume() 中重新打开。而申请的弹出框会导致 activity 的 onResume 重复调用，针对这种情况需要做好处理。

以上就是关于 zxing 的简单集成的所有内容，源码已经放在了 GitHub 上，仅供参考。[commonTest-zxing](https://github.com/maintel/CommonTest/tree/master/zxing)

# 参考

- [zxing 官方文档](https://github.com/zxing/zxing/wiki/Getting-Started-Developing)
- [zxing-android](https://github.com/zxing/zxing/tree/master/android)