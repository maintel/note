viewGroup 继承自 view

view 的 requestLayout

```java
//从源码注释可以看出，如果当前View在请求布局的时候，View树正在进行布局流程的话，
//该请求会延迟到布局流程完成后或者绘制流程完成且下一次布局发现的时候再执行。
@CallSuper
public void requestLayout() {
    if (mMeasureCache != null) mMeasureCache.clear();

    if (mAttachInfo != null && mAttachInfo.mViewRequestingLayout == null) {
        // Only trigger request-during-layout logic if this is the view requesting it,
        // not the views in its parent hierarchy
        ViewRootImpl viewRoot = getViewRootImpl();
        if (viewRoot != null && viewRoot.isInLayout()) {
            if (!viewRoot.requestLayoutDuringLayout(this)) {
                return;
            }
        }
        mAttachInfo.mViewRequestingLayout = this;
    }

    //为当前view设置标记位 PFLAG_FORCE_LAYOUT
    mPrivateFlags |= PFLAG_FORCE_LAYOUT;
    mPrivateFlags |= PFLAG_INVALIDATED;

    if (mParent != null && !mParent.isLayoutRequested()) {
        //向父容器请求布局
        mParent.requestLayout();
    }
    if (mAttachInfo != null && mAttachInfo.mViewRequestingLayout == this) {
        mAttachInfo.mViewRequestingLayout = null;
    }
}
```

关于 mParent 的赋值

```java
void assignParent(ViewParent parent) {
        if (mParent == null) {
            mParent = parent;
        } else if (parent == null) {
            mParent = null;
        } else {
            throw new RuntimeException("view " + this + " being added, but"
                    + " it already has a parent");
        }
    }
```
ViewParent 是一个接口，继承了这个接口的类有两个 ViewGroup 和 ViewRootImpl

assignParent 的调用位置有 viewRootImpl 和 ViewGroup。ViewGroup 的 assignParent 是在 ViewGroup.addView 时被调用的，他的最终实现还是 ViewRootImpl。

不论如何吧，view 的父 View 可能是一个 View 或者是一个 ViewGroup，这样一层一层的向上找的话，最终会找到 DecorView（我们当然知道 DecorView 是所有 View 的根 View ）。

关于 DecorView 了解了 window 的添加过程以及 activity 的启动过程就能知道，DecorView 的父 View 是 ViewRootImpl。

所以 requestLayout 的最终实现是在 ViewRootImpl 中的。

```java
    public void requestLayout() {
        if (!mHandlingLayoutInLayoutRequest) {
            checkThread();
            mLayoutRequested = true;
            scheduleTraversals();
        }
    }
```
scheduleTraversals 最终会调用 measure、layout、draw 的流程。
