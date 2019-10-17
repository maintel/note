可以知道的是 Android 中的所有视图都是通过 Window 来呈现的，Window 是 View 的管理者。

向 Window 添加 View 是通过 WindowManager 来实现的。

WindowManager 是一个接口，并且继承自 ViewManager。

关于 ViewManager

```java
public interface ViewManager{
    public void addView(View view, ViewGroup.LayoutParams params);
    public void updateViewLayout(View view, ViewGroup.LayoutParams params);
    public void removeView(View vaiew);
}
```

可以看到只有三个方法，添加、更新、删除 View。

WindowManager 也是一个接口，它的实现类是 WindowManagerImpl。查看 WindowManagerImpl

```java
public final class WindowManagerImpl implements WindowManager {
    private final WindowManagerGlobal mGlobal = WindowManagerGlobal.getInstance();

    @Override
    public void addView(@NonNull View view, @NonNull ViewGroup.LayoutParams params) {
        applyDefaultToken(params);
        mGlobal.addView(view, params, mContext.getDisplay(), mParentWindow);
    }

    @Override
    public void updateViewLayout(@NonNull View view, @NonNull ViewGroup.LayoutParams params) {
        applyDefaultToken(params);
        mGlobal.updateViewLayout(view, params);
    }

    @Override
    public void removeView(View view) {
        mGlobal.removeView(view, false);
    }
}
```

可以看到 WindowManagerImpl 也没有实现视图的添加、更新、删除，而是交给了 WindowManagerGlobal 来处理，继续追踪。找到 WindowManagerGlobal.addView()

```java
public void addView(View view, ViewGroup.LayoutParams params,
            Display display, Window parentWindow) {
        //  首先检查合法性
        if (view == null) {
            throw new IllegalArgumentException("view must not be null");
        }
        if (display == null) {
            throw new IllegalArgumentException("display must not be null");
        }
        if (!(params instanceof WindowManager.LayoutParams)) {
            throw new IllegalArgumentException("Params must be WindowManager.LayoutParams");
        }

        // 检查父级 View 是否存在
        final WindowManager.LayoutParams wparams = (WindowManager.LayoutParams) params;
        if (parentWindow != null) {
            // adjustLayoutParamsForSubWindow 从字面意思是调整窗口布局参数
            parentWindow.adjustLayoutParamsForSubWindow(wparams);
        } else {
            // If there's no parent, then hardware acceleration for this view is
            // set from the application's hardware acceleration setting.
            final Context context = view.getContext();
            if (context != null
                    && (context.getApplicationInfo().flags
                            & ApplicationInfo.FLAG_HARDWARE_ACCELERATED) != 0) {
                wparams.flags |= WindowManager.LayoutParams.FLAG_HARDWARE_ACCELERATED;
            }
        }

        ViewRootImpl root;
        View panelParentView = null;

        synchronized (mLock) {
            // Start watching for system property changes.
            if (mSystemPropertyUpdater == null) {
                mSystemPropertyUpdater = new Runnable() {
                    @Override public void run() {
                        synchronized (mLock) {
                            for (int i = mRoots.size() - 1; i >= 0; --i) {
                                mRoots.get(i).loadSystemProperties();
                            }
                        }
                    }
                };
                SystemProperties.addChangeCallback(mSystemPropertyUpdater);
            }

            // 检测是否已经存在这个 view
            int index = findViewLocked(view, false);
            if (index >= 0) {
                // 如果已经存在但是是快要移除的 view 就 移除它
                if (mDyingViews.contains(view)) {
                    // Don't wait for MSG_DIE to make it's way through root's queue.
                    mRoots.get(index).doDie();
                } else {
                    // 否则抛出异常
                    throw new IllegalStateException("View " + view
                            + " has already been added to the window manager.");
                }
                // The previous removeView() had not completed executing. Now it has.
            }

            // If this is a panel window, then find the window it is being
            // attached to for future reference.
            if (wparams.type >= WindowManager.LayoutParams.FIRST_SUB_WINDOW &&
                    wparams.type <= WindowManager.LayoutParams.LAST_SUB_WINDOW) {
                final int count = mViews.size();
                for (int i = 0; i < count; i++) {
                    if (mRoots.get(i).mWindow.asBinder() == wparams.token) {
                        panelParentView = mViews.get(i);
                    }
                }
            }

            // 创建 ViewRootImpl
            root = new ViewRootImpl(view.getContext(), display);

            view.setLayoutParams(wparams);

            mViews.add(view);
            mRoots.add(root);
            mParams.add(wparams);
        }

        // do this last because it fires off messages to start doing things
        try {
            // 最终是通过 ViewRootImpl 的 setView 方法来添加View
            root.setView(view, wparams, panelParentView);
        } catch (RuntimeException e) {
            // BadTokenException or InvalidDisplayException, clean up.
            synchronized (mLock) {
                final int index = findViewLocked(view, false);
                if (index >= 0) {
                    removeViewLocked(index, true);
                }
            }
            throw e;
        }
    }
```

经过上面的分析可以知道，最终是通过 ViewRootImpl.setView() 方法来添加

```java
public void setView(View view, WindowManager.LayoutParams attrs, View panelParentView) {
    ...
    // 通过requestLayout来刷新视图并完成绘制
    requestLayout();
    ...
    collectViewAttributes();
    // 通过mWindowSession.addToDisplay 来进行显示
    res = mWindowSession.addToDisplay(mWindow, mSeq, mWindowAttributes,
            getHostVisibility(), mDisplay.getDisplayId(),
            mAttachInfo.mContentInsets, mAttachInfo.mStableInsets,
            mAttachInfo.mOutsets, mInputChannel);
    ...
}
```

在 ViewRootImpl 中 mWindowSession 初始化

```java
IWindowSession mWindowSession = WindowManagerGlobal.getWindowSession();
```
IWindowSession 是一个 Binder 对象，所以在添加过程中进行了 IPC 调用

```java
public static IWindowSession getWindowSession() {
        synchronized (WindowManagerGlobal.class) {
            ...
            // 获取 WindowManagerService
            IWindowManager windowManager = getWindowManagerService();
            sWindowSession = windowManager.openSession()
            ...     
            }
            return sWindowSession;
        }
}

//WindowManagerService.openSession
 @Override
public IWindowSession openSession(IWindowSessionCallback callback, IInputMethodClient client,
        IInputContext inputContext) {
    if (client == null) throw new IllegalArgumentException("null client");
    if (inputContext == null) throw new IllegalArgumentException("null inputContext");
    Session session = new Session(this, callback, client, inputContext);
    return session;
}
```
可以看到上面的 mWindowSession 对象真正实现是一个 Session。那就可以继续追踪到 Session.addToDisplay()

```java

    final WindowManagerService mService;

    @Override
    public int addToDisplay(IWindow window, int seq, WindowManager.LayoutParams attrs,
            int viewVisibility, int displayId, Rect outContentInsets, Rect outStableInsets,
            Rect outOutsets, InputChannel outInputChannel) {
        return mService.addWindow(this, window, seq, attrs, viewVisibility, displayId,
                outContentInsets, outStableInsets, outOutsets, outInputChannel);
    }
```

通过上面的代码可以看到，最终是通过 WindowManagerService.addWindow 来进行添加。至于 WindowManagerService 怎么处理的暂时不做深入了，太长了这个方法...
