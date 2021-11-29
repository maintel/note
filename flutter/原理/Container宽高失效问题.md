请牢记 flutter 的布局计算方式是，约束向下传递，宽高向上传递。

https://zhuanlan.zhihu.com/p/41801871

即 父 widget 告诉子 widget 宽高的约束方式， 子 widget 告诉父 widget 自己所需的宽高。

https://mp.weixin.qq.com/s/nkjPIgNRazW56bHuh0PEXQ

- Widget 只能在父级（Parent）的限制内决定自身的大小。这意味着 Widget 通常不能拥有它想要的任意大小。

- Widget 不知道也无法确定其在屏幕上的位置，因为它的位置是由父级（Parent）决定的。

- 由于父级（Parent）的大小和位置又取决于其父级（Parent），因此只有考虑整个布局树的情况下才能精确定义所有 Widget 的大小和位置。