commit

FragmentTransaction.commitInternal 的实现在  BackStackState.commitAllowingStateLoss 

最终调用了 BackStackState.commitInternal 方法在此方法中执行了：

```java
        if (mAddToBackStack) {
            mIndex = mManager.allocBackStackIndex(this);  
        } else {
            mIndex = -1;
        }
        mManager.enqueueAction(this, allowStateLoss);
```

mManager 是 FragmentManager，它的实现是 FragmentManagerImpl

其中 FragmentManager.allocBackStackIndex 方法是将 fragment 放入到回退栈中 （mAddToBackStack 参数通过 fragmentTransaction.addToBackStack 来设置。）

然后它调用了 FragmentManager.enqueueAction 方法，

```java
    public void enqueueAction(OpGenerator action, boolean allowStateLoss) {
        synchronized (this) {
            ...
            mPendingActions.add(action);
            scheduleCommit();
        }
    }
```

在 enqueueAction 中它将待执行的动作放在了等待列表中，然后它调用了 FragmentManager.scheduleCommit 方法

```java
    private void scheduleCommit() {
        synchronized (this) {
            boolean postponeReady =
                    mPostponedTransactions != null && !mPostponedTransactions.isEmpty();
            boolean pendingReady = mPendingActions != null && mPendingActions.size() == 1;
            if (postponeReady || pendingReady) {
                mHost.getHandler().removeCallbacks(mExecCommit);
                mHost.getHandler().post(mExecCommit);
            }
        }
    }
```

这个方法就是执行了 mExecCommit ，它是一个 runable 对象

```java
    Runnable mExecCommit = new Runnable() {
        @Override
        public void run() {
            execPendingActions();
        }
    };
```

里面也只是执行了一个 execPendingActions 方法。