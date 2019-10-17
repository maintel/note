

# 关于obtainStyledAttributes方法的说明

[参考地址](http://www.jianshu.com/p/61b79e7f88fc)

有如下重载

- obtainStyledAttributes(int[] attrs)

- obtainStyledAttributes(int resid, int[] attrs)

- obtainStyledAttributes(AttributeSet set, int[] attrs)

- obtainStyledAttributes(AttributeSet set, int[] attrs, int defStyleAttr, int defStyleRes)

这个方法是干嘛的呢？

    其实就是用来获取我们定义的属性，只不过根据不同的重载，获取的方法以及来源也不太一样。

