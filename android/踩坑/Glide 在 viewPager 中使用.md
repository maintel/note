

 # 当给图片设置为 bitmap 的时候

 // glide 会返回一个相同的 bitmap 对象，这个时候会导致一个结果：
                // 之前的因为生命周期的原因，当翻页以后 前面或者后面页面中引用的 bitmap 对象被销毁（其实也并没有被回收，因为这个bitmap 对象并不为空，而是 buffer 为空），
                // 然后再回来的时候后面就获取不到这个 bitmap 对象了。
                // 至于为什么直接设置into（imageview） 没有问题，是因为 glide 内部标记了 tag，
                // note  所以这里先进行一次拷贝，这样就保证了 glide 缓存的对象 bitmap 不被回收掉
//                mImageView.setImageBitmap();
                mImageView.initImageView(((GlideBitmapDrawable) resource).getBitmap().copy(Bitmap.Config.ARGB_8888, true), false);