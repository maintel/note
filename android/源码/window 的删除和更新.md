window 的删除和更新过程是和添加类似的，分析了添加的过程，删除和更新已经很明了。

# 删除

和添加一样，也是通过 WindowManagerImpl，然后在委托给 WindowManagerGlobal 的 removeView 方法实现。

WindowManagerImpl 提供了两种删除 view 的方法，分别为同步和异步：

```java

    // 异步删除
    @Override
    public void removeView(View view) {
        mGlobal.removeView(view, false);
    }

    // 同步删除
    @Override
    public void removeViewImmediate(View view) {
        mGlobal.removeView(view, true);
    }
```

WindowManagerGlobal 的 removeView 方法如下：

```java
    public void removeView(View view, boolean immediate) {
		// 先检测是否为空
        if (view == null) {
            throw new IllegalArgumentException("view must not be null");
        }

        synchronized (mLock) {
			//从mViews 列表中找到当前view的位置
            int index = findViewLocked(view, true);
			//从 ViewRootImpl 中获取到被添加的view
            View curView = mRoots.get(index).getView();
            // 在这里做进一步的删除
            removeViewLocked(index, immediate);
            // 如果从 ViewRootImpl 获取到的 view 和要移除的view一样就返回，否则抛出异常
            if (curView == view) {
                return;
            }

            throw new IllegalStateException("Calling with view " + view
                    + " but the ViewAncestor is attached to " + curView);
        }
    }
```
removeView 中没有做具体的删除操作，而是做了一些检测以及查找工作，然后交给了 removeViewLocked 继续，进入这个方法看看：

```java
    private void removeViewLocked(int index, boolean immediate) {
        ViewRootImpl root = mRoots.get(index);
        View view = root.getView();

        if (view != null) {
            //关闭软键盘
            InputMethodManager imm = InputMethodManager.getInstance();
            if (imm != null) {
                imm.windowDismissed(mViews.get(index).getWindowToken());
            }
        }
        // 发送删除消息
        boolean deferred = root.die(immediate);
        if (view != null) {
            view.assignParent(null);
            if (deferred) {
                // mDyingViews 是待删除view的列表
                // 这里的的逻辑是如果是异步删除就将view添加到待被删除的列表中（为什么是这样继续向下看 die 方法）
                mDyingViews.add(view);
            }
        }
    }
```
removeViewLocked 方法也非常简单，可以看到它调用了当前 view 对应的 ViewRootImpl 的 die 方法，然后它也没有真正实现删除操作，那么就进入这个方法看一看：

```java
    /**
     * @param immediate True, do now if not in traversal. False, put on queue and do later.
     * @return True, request has been queued. False, request has been completed.
     */
    boolean die(boolean immediate) {
        // Make sure we do execute immediately if we are in the middle of a traversal or the damage
        // done by dispatchDetachedFromWindow will cause havoc on return.
        //如果是同步删除，并且没有在遍历执行中则执行 doDie 方法立即删除
        if (immediate && !mIsInTraversal) {
            doDie();
            return false;
        }
        // 如果没有在绘制就销毁渲染器
        if (!mIsDrawing) {
            destroyHardwareRenderer();
        } else {
            Log.e(mTag, "Attempting to destroy the window while drawing!\n" +
                    "  window=" + this + ", title=" + mWindowAttributes.getTitle());
        }
        //发送消息进行异步删除。
        mHandler.sendEmptyMessage(MSG_DIE);
        return true;
    }
```

可以看到同步删除和异步删除的逻辑是不同的，同步删除立即调用了 doDie 方法，异步删除则通过 handler 发送了 MSG_DIE 消息。在 handler 接收了消息后也立马调用了 doDie 方法。因为handler内部是队列的形式来处理消息，所以异步删除调用 doDie 的时机要比同步删除稍晚一些，所以异步删除立即返回了 true 并且在 WindowManagerGlobal.removeViewLocked 方法中将要删除的 view 添加到了 mDyingViews 列表中。

    回忆添加 view 的过程在 WindowManagerGlobal.addView 中对 mDyingViews 有一个检测。

那么删除 view 的操作应该是在 ViewRootImpl.doDie 中执行的了？继续查看 ViewRootImpl.doDie 方法:

```java
  void doDie() {
        // 检查调用线程 只有创建 view 的线程才能修改它（奇怪的是它并没有检测说必须要在主线程？）
        checkThread();
        
        synchronized (this) {
            if (mRemoved) {
                return;
            }
            mRemoved = true;
            //mAdded 在 setView 方法中会被设为 true
            if (mAdded) {
                // 调用此方法来进行删除操作
                dispatchDetachedFromWindow();
            }
            ...

            mAdded = false;
        }
        // 最终调用 WindowManagerGlobal的doRemoveView方法来删除数据
        WindowManagerGlobal.getInstance().doRemoveView(this);
    }
```

在 doDie 中也没有完成真正的删除操作，而是调用了 ViewRootImpl.dispatchDetachedFromWindow 方法并且最终调用了 WindowManagerGlobal 的 doRemoveView 方法。

先查看 dispatchDetachedFromWindow：

```java
// 这里只列出部分代码
    void dispatchDetachedFromWindow() {
        if (mView != null && mView.mAttachInfo != null) {
            mAttachInfo.mTreeObserver.dispatchOnWindowAttachedChange(false);
            // 调用了 view 的dispatchDetachedFromWindow方法
            mView.dispatchDetachedFromWindow();
        }

        ...
        //清除相关数据、消息、回调等
        mView.assignParent(null);
        mView = null;
        mAttachInfo.mRootView = null;
        mSurface.release();

        ...
        try {
            // 通过 IPC 机制删除 window
            mWindowSession.remove(mWindow);
        } catch (RemoteException e) {
        }

        ...
    }
```

可以看到 ViewRootImpl.dispatchDetachedFromWindow 方法主要做了三件事情：

- 调用了 view 的 dispatchDetachedFromWindow 方法，在 view.dispatchDetachedFromWindow 方法中，主要有两个回调 `onDetachedFromWindow`和`onDetachedFromWindowInternal`，这些就是我们常用的监听，可以在里面做一些自己的资源回收工作。
- 清除数据、消息、回调等。
- 调用 session 的 remove 方法，和添加一样最终它会调用 WindowManagerService 的 removeWindow 方法。

同时在 doDie 的最后还调用了  WindowManagerGlobal 的 doRemoveView 方法，这个方法很简单:

```java
    void doRemoveView(ViewRootImpl root) {
        synchronized (mLock) {
            final int index = mRoots.indexOf(root);
            if (index >= 0) {
                mRoots.remove(index);
                mParams.remove(index);
                final View view = mViews.remove(index);
                mDyingViews.remove(view);
            }
        }
        if (ThreadedRenderer.sTrimForeground && ThreadedRenderer.isAvailable()) {
            doTrimForeground();
        }
    }
```

在 doRemoveView 方法中清除了和要删除的 view 相关的一切数据。

至此 window删除 的删除过程就全部完成，也很简单，用一个图来简单表示：

![window删除](http://blogqn.maintel.cn/window删除view的过程.png?e=3108646682&token=kDSqSAyKGaf8JcHprWP7S4W3hGuz8kDIEhzAufWH:PMi8HPns6kcHnYze1rvLv436uzo=)