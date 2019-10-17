window 和 view 的关系

window 是一个抽象的概念，在 IPC 通讯过程中他是一个 IWindow 的 binder 对象，

它和 view 应该是一一对应的关系，每个 View 都对应有一个 window ， window 的具体对象是 ViewRootImpl 的一个内部类叫 W

```java
 static class W extends IWindow.Stub {
        private final WeakReference<ViewRootImpl> mViewAncestor;
        private final IWindowSession mWindowSession;
 }

 ```

 它内部持有了对当前 viewRootImpl 的弱引用，以及一个 session 对象。通过它来完成了 IPC 通讯，然后调用了 viewRootImpl 的具体方法。

 而比如 在 window 创建过程中，viewRootImpl.setView 的过程它传递给 Session 的是一个 window 对象而不是当前 view 本身。可以看 addToDisplay 方法知道。

 ```java
public void setView(View view, WindowManager.LayoutParams attrs, View panelParentView) {
    // 通过mWindowSession.addToDisplay 来进行显示
    res = mWindowSession.addToDisplay(mWindow, mSeq, mWindowAttributes,
            getHostVisibility(), mDisplay.getDisplayId(),
            mAttachInfo.mContentInsets, mAttachInfo.mStableInsets,
            mAttachInfo.mOutsets, mInputChannel);
    ...
}
 ```

这也就解释了为什么删除过程时为什么是通过 IPC 机制来移除 window 而不是具体的 view 对象。

这里的 view 并不是指的某一个控件，而是视图的意思，比如一个 activity 、dialog、popupWindow、Toast 等。


所以  view 是不能单独存在的，它是依附在 window 上。