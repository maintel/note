<!-- TOC -->

- [占了多大内存？](#占了多大内存)
- [举个例子](#举个例子)
- [怎么计算的](#怎么计算的)
    - [Bitmap 的生成](#bitmap-的生成)
    - [获取大小](#获取大小)
- [所以呢大小怎么算？](#所以呢大小怎么算)
- [网络图片大小](#网络图片大小)

<!-- /TOC -->

# 占了多大内存？

首先这里要明确的是

- 占用内存

- 图片大小

以上两者是不同的，占用内存表示图片被加载进来以后占用的内存空间大小，图片大小则是图片在磁盘存储时占用的大小。

两者之间有什么关系么？下面再讲。

获取一个biemap占用多大内存空间的方法如下：

```java
       int sizeOf = bitmap.getRowBytes() * bitmap.getHeight();
       //getRowBytes 表示一行的字节数，getHeight可以认为总共有多少行。
```

# 举个例子

现在有一个1080*1920大小26.6K的图片放在xxhdpi文件夹中加载到内存中，获取到的大小为：

    8294400 B = 7.9 MB

为什么会这么大？

实际上是因为  1080 * 1920 * 4

为什么要乘以四，因为图片的大小不但和像素有关还和色彩格式有关ARGB_8888一个像素占用四个字节。

同时还与图片所在的资源目录有关

测试手机为 1+3T  1920 * 1080  5.5寸  像素密度为 400 ==> xxhdpi，

而如果放在xhdpi下 则为 1080 * 1.5 * 1920 * 1.5 *4 = 18662400 至于为什么这么算请看下面。

# 怎么计算的

先说结论Bitmap在内存当中占用的大小其实取决于以下三点：

- 色彩格式
- 原始文件存放的资源目录
- 目标屏幕的密度

## Bitmap 的生成

关于 bitmap 的原理网上有很多文章这里就不在讲了，可以参考[这里](https://zhuanlan.zhihu.com/p/31450987)，其中在生成过程中有下面的关键代码。

```c++
outputBitmap->setInfo(SkImageInfo::Make(scaledWidth, scaledHeight,
                colorType, decodingBitmap.alphaType()));
```
可以看到最终输出的 outputBitmap 的大小是 scaledWidth*scaledHeight，把这两个变量计算的片段拿出来给大家一看就明白了：

```c++
if (willScale && decodeMode != SkImageDecoder::kDecodeBounds_Mode) {
     scaledWidth = int(scaledWidth * scale + 0.5f);
     scaledHeight = int(scaledHeight * scale + 0.5f);
}
```
其中 scale 的大小是这样得来的：

```c++
if (density != 0 && targetDensity != 0 && density != screenDensity) {
                scale = (float) targetDensity / density;
    }
```
scale 是由 density 和 targetDensity 得来的，前者是 decodingBitmap 的 density，这个值跟这张图片的放置的目录有关，后者是目标的 density，它的值和当前设备的屏幕密度有关，比如例子中的1+3T就属于 xxhdpi 则值为480。

到这里我们就知道一个图片的宽高值了，那图片的大小是不是就是 width * height 呢？显然不是，接着往下看。

## 获取大小

获取大小的方法在最上面我们就讲了，获取一个biemap占用多大内存空间的方法如下：

```java
       int sizeOf = bitmap.getRowBytes() * bitmap.getHeight();
       //getRowBytes 表示一行的字节数，getHeight可以认为总共有多少行。
```
getHeight 就是获取高度单位是（px），getRowBytes 又是什么?

```java
public final int getRowBytes() {
    if (mRecycled) {
        Log.w(TAG, "Called getRowBytes() on a recycle()'d bitmap! This is undefined behavior!");
    }
    return nativeRowBytes(mFinalizer.mNativeBitmap);
}
```
可以看到它最终到 jni 里面了。

```c++
{   "nativeRowBytes",           "(J)I", (void*)Bitmap_rowBytes }

static jint Bitmap_rowBytes(JNIEnv* env, jobject, jlong bitmapHandle) {
    SkBitmap* bitmap = reinterpret_cast<SkBitmap*>(bitmapHandle);
    return static_cast<jint>(bitmap->rowBytes());
}
```

可以看到 bitmap 的实际类型是一个 SkBitmap，

```c++
    /** Return the number of bytes between subsequent rows of the bitmap. */
   size_t rowBytes() const { return fRowBytes; }

   /** SKbitmap.cpp */

   size_t SkBitmap::ComputeRowBytes(Config c, int width) {
        return SkColorTypeMinRowBytes(SkBitmapConfigToColorType(c), width);
    }
```
SkImageInfo.h
```c++
// 不同色彩格式所占的字节数
static int SkColorTypeBytesPerPixel(SkColorType ct) {
    static const uint8_t gSize[] = {
        0,  // Unknown
        1,  // Alpha_8
        2,  // RGB_565
        2,  // ARGB_4444
        4,  // RGBA_8888
        4,  // BGRA_8888
        1,  // kIndex_8
    };
    SK_COMPILE_ASSERT(SK_ARRAY_COUNT(gSize) == (size_t)(kLastEnum_SkColorType + 1),
                      size_mismatch_with_SkColorType_enum);

    SkASSERT((size_t)ct < SK_ARRAY_COUNT(gSize));
    return gSize[ct];
}

// getRowBytes 的返回值
static inline size_t SkColorTypeMinRowBytes(SkColorType ct, int width) {
    return width * SkColorTypeBytesPerPixel(ct);
}
```
最终可以追踪到 getRowBytes 的值为 宽度 * 字节数。
# 所以呢大小怎么算？

所以可以得出一个公式，一个本地资源的图片放在内存中的大小为：

    int(width * targetDensity/density + 0.5f) * int(height * targetDensity/density + 0.5) * gSize

targetDensity 为当前设备的 dpi，density 为图片原始 dpi，gSize 的值就和图片的色彩格式有关，具体对应关系如下：

|色彩格式|字节数|
|:-----|:----|
|Alpha_8|1|
|RGB_565|2|
|ARGB_4444|2|
|RGBA_8888|4|
|BGRA_8888|4|
|kIndex_8|1|
|Unknown|0|

屏幕密度对应关系：

||dpi|比例|
|:--|:--|:--|
|ldpi|120|0.75|
|mdpi|160|1|
|hdpi|240|1.5|
|xhdpi|320|2.0|
|xxhdpi|480|3.0|
|xxxhdpi|640|4.0|

上面的公式很好理解，如果要要在一个 xxxhdpi 的设备上加载一个放在 xxhdpi 中的大小为 768 * 960 的 png 图片时内存大小就是

    int(768 * 640/480 + 0.5f）* int(960 * 640/480 + 0.5f) * 4
# 网络图片大小

上面讲了本地图片加载到内存中以后所占空间的计算方法，那如果是网络图片呢，由于它没有原始 dpi，所以默认的和当前设备 dpi 一致，因此如果未做处理的情况下一个图片的大小应该为： 

    width * height * gsize
 