# 使用软引用和弱引用

场景：

    为了防止内存溢出，在处理一些占用内存大而且声明周期较长的对象时候，可以尽量应用软引用和弱引用技术。

例如：

应用程序用使用了大量的默认图片，这些图片在很多地方都会用到，如果每次都去读取图片则速度较慢，这时我们可以考虑将图片缓存起来，但是缓存大量的图片又会占用大量的内存，容易发生OOM。这时候就可以考虑使用软引用了。

使用一个MAP将bitmap的软引用缓存下来：

```java
    private Map<String,SoftReference<Bitmap>> bitmapMap = new HashMap<>();

    public void addBitmapCache(String path) {
        Bitmap bitmap = BitmapFactory.decodeFile(path);
        SoftReference<Bitmap> softReference = new SoftReference<Bitmap>(bitmap);
        bitmapMap.put(path, softReference);
    }
```

当获取的时候可以使用如下方法：

```java
    
    public Bitmap getBitmapByPath(String path) {
        // 从缓存中取软引用的Bitmap对象
        SoftReference<Bitmap> softBitmap = imageCache.get(path);
        // 判断是否存在软引用
        if (softBitmap == null) {
            return null;
        }
        // 取出Bitmap对象，如果由于内存不足Bitmap被回收，将取得空
        Bitmap bitmap = softBitmap.get();
        return bitmap;
    }
```

当取出的时候一定要注意判空，如果为空则重新加载并缓存。

