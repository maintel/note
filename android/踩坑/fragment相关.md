# 关于 Fragment already added 的研究

    java.lang.IllegalStateException: Fragment already added: ParentFragment{ecd4346 #2 id=0x7f090035 2131297297}
    at android.support.v4.app.FragmentManagerImpl.addFragment(apmsdk:1882)
    at android.support.v4.app.BackStackRecord.executeOps(apmsdk:762)
    at android.support.v4.app.FragmentManagerImpl.executeOps(apmsdk:2580)
    at android.support.v4.app.FragmentManagerImpl.executeOpsTogether(apmsdk:2367)
    at android.support.v4.app.FragmentManagerImpl.removeRedundantOperationsAndExecute(apmsdk:2322)
    at android.support.v4.app.FragmentManagerImpl.execPendingActions(apmsdk:2229)
    at android.support.v4.app.FragmentManagerImpl$1.run(apmsdk:700)
    at android.os.Handler.handleCallback(Handler.java:907)




首先应该研究一下 add 方法

```java
fragmentTransaction
            .hide(this.mCurrentFragment)
            .add(R.id.activity_main_fragment_container, fragment, this.mLastSelectFragmentTag + "")

// 调用 BackStackRecord.add

    @Override
    public FragmentTransaction add(int containerViewId, Fragment fragment, String tag) {
        doAddOp(containerViewId, fragment, tag, OP_ADD);
        return this;
    }

    private void doAddOp(int containerViewId, Fragment fragment, String tag, int opcmd) {
        //...
        addOp(new Op(opcmd, fragment));
    }

//    ArrayList<Op> mOps = new ArrayList<>();
    void addOp(Op op) {
        mOps.add(op);
        op.enterAnim = mEnterAnim;
        op.exitAnim = mExitAnim;
        op.popEnterAnim = mPopEnterAnim;
        op.popExitAnim = mPopExitAnim;
    }
```

其实就是把要添加的 fragment 添加到一个 list 中，

然后再看 commitAllowingStateLoss

调用顺序

```java
        fragmentTransaction
                .hide(this.mCurrentFragment)
                .add(R.id.activity_main_fragment_container, fragment,this.mLastSelectFragmentTag + "")
                .show(fragment)
                .commitAllowingStateLoss();

    //调用 BackStackState.commitAllowingStateLoss
    @Override
    public int commitAllowingStateLoss() {
        return commitInternal(true);
    }

    int commitInternal(boolean allowStateLoss) {
        // 首先检查是否 添加过了
        if (mCommitted) throw new IllegalStateException("commit already called");
        if (FragmentManagerImpl.DEBUG) {
            Log.v(TAG, "Commit: " + this);
            LogWriter logw = new LogWriter(TAG);
            PrintWriter pw = new PrintWriter(logw);
            dump("  ", null, pw, null);
            pw.close();
        }
        //将添加过的标记设置为 true
        mCommitted = true;
        if (mAddToBackStack) {
            mIndex = mManager.allocBackStackIndex(this);
        } else {
            mIndex = -1;
        }
        //调用 FragmentManagerImpl.enqueueAction
        mManager.enqueueAction(this, allowStateLoss);
        return mIndex;
    }

    //FragmentManagerImpl
    public void enqueueAction(OpGenerator action, boolean allowStateLoss) {
        //allowStateLoss == true
        if (!allowStateLoss) {
            checkStateLoss();
        }
        synchronized (this) {
            if (mDestroyed || mHost == null) {
                if (allowStateLoss) {
                    // This FragmentManager isn't attached, so drop the entire transaction.
                    return;
                }
                throw new IllegalStateException("Activity has been destroyed");
            }
            if (mPendingActions == null) {
                mPendingActions = new ArrayList<>();
            }
            // 将之前的调用 add 方法的结果添加到 mPendingActions 等待后续执行
            mPendingActions.add(action);
            scheduleCommit();
        }
    }

    //FragmentManagerImpl  等待执行提交，它最终会通过 handler 使 mExecCommit 执行
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

    // 看看 mExecCommit 是啥
    Runnable mExecCommit = new Runnable() {
        @Override
        public void run() {
            execPendingActions();
        }
    };
    /**
     * Only call from main thread!
     */
    public boolean execPendingActions() {
        ensureExecReady(true);

        boolean didSomething = false;
        //
        while (generateOpsForPendingActions(mTmpRecords, mTmpIsPop)) {
            mExecutingActions = true;
            try {
                // 删除冗余操作并执行
                removeRedundantOperationsAndExecute(mTmpRecords, mTmpIsPop);
            } finally {
                cleanupExec();
            }
            didSomething = true;
        }

        doPendingDeferredStart();
        burpActive();

        return didSomething;
    }

    //这一步是获取需要执行的内容，
    private boolean generateOpsForPendingActions(ArrayList<BackStackRecord> records,
            ArrayList<Boolean> isPop) {
        boolean didSomething = false;
        synchronized (this) {
            if (mPendingActions == null || mPendingActions.size() == 0) {
                return false;
            }

            final int numActions = mPendingActions.size();
            for (int i = 0; i < numActions; i++) {
                // generateOps 调用了BackStackRecord.generateOps 方法
                didSomething |= mPendingActions.get(i).generateOps(records, isPop);
            }
            mPendingActions.clear();
            mHost.getHandler().removeCallbacks(mExecCommit);
        }
        return didSomething;
    }

    //BackStackRecord.generateOps(mTmpRecords, mTmpIsPop)
    // 这一步的操作使将 操作内容添加到 mTmpRecords 中
    @Override
    public boolean generateOps(ArrayList<BackStackRecord> records, ArrayList<Boolean> isRecordPop) {
        if (FragmentManagerImpl.DEBUG) {
            Log.v(TAG, "Run: " + this);
        }

        records.add(this);
        isRecordPop.add(false);
        if (mAddToBackStack) {
            mManager.addBackStackState(this);
        }
        return true;
    }

    // 这个方法就是将多个同样的操作合并成一个，并且执行他们，例如有两个同样的提交会被合并并且执行
    private void removeRedundantOperationsAndExecute(ArrayList<BackStackRecord> records,
            ArrayList<Boolean> isRecordPop) {
        if (records == null || records.isEmpty()) {
            return;
        }

        if (isRecordPop == null || records.size() != isRecordPop.size()) {
            throw new IllegalStateException("Internal error with the back stack records");
        }

        // Force start of any postponed transactions that interact with scheduled transactions:
        executePostponedTransaction(records, isRecordPop);

        final int numRecords = records.size();
        int startIndex = 0;
        for (int recordNum = 0; recordNum < numRecords; recordNum++) {
            final boolean canReorder = records.get(recordNum).mReorderingAllowed;
            if (!canReorder) {
                // execute all previous transactions
                if (startIndex != recordNum) {
                    // 执行
                    executeOpsTogether(records, isRecordPop, startIndex, recordNum);
                }
                // execute all pop operations that don't allow reordering together or
                // one add operation
                int reorderingEnd = recordNum + 1;
                if (isRecordPop.get(recordNum)) {
                    while (reorderingEnd < numRecords
                            && isRecordPop.get(reorderingEnd)
                            && !records.get(reorderingEnd).mReorderingAllowed) {
                        reorderingEnd++;
                    }
                }
                executeOpsTogether(records, isRecordPop, recordNum, reorderingEnd);
                startIndex = reorderingEnd;
                recordNum = reorderingEnd - 1;
            }
        }
        if (startIndex != numRecords) {
            executeOpsTogether(records, isRecordPop, startIndex, numRecords);
        }
    }

    private void executeOpsTogether(ArrayList<BackStackRecord> records,
            ArrayList<Boolean> isRecordPop, int startIndex, int endIndex) {
        //...
        executeOps(records, isRecordPop, startIndex, endIndex);

        //...
    }

    // 最终调用了 executeOps，
    private static void executeOps(ArrayList<BackStackRecord> records,
            ArrayList<Boolean> isRecordPop, int startIndex, int endIndex) {
        for (int i = startIndex; i < endIndex; i++) {
            final BackStackRecord record = records.get(i);
            final boolean isPop = isRecordPop.get(i);
            //由 BackStackRecord.generateOps 可知 isPop 为 false
            if (isPop) {
                record.bumpBackStackNesting(-1);
                // Only execute the add operations at the end of
                // all transactions.
                boolean moveToState = i == (endIndex - 1);
                record.executePopOps(moveToState);
            } else {
                record.bumpBackStackNesting(1);
                // 最终执行 BackStackRecord.executeOps 方法
                record.executeOps();
            }
        }
    }

    //BackStackRecord
    void executeOps() {
        final int numOps = mOps.size();
        for (int opNum = 0; opNum < numOps; opNum++) {
            final Op op = mOps.get(opNum);
            final Fragment f = op.fragment;
            if (f != null) {
                f.setNextTransition(mTransition, mTransitionStyle);
            }
            switch (op.cmd) {
                case OP_ADD:
                    f.setNextAnim(op.enterAnim);
                    // 最终调用了 FragmentManagerImpl.addFragment 方法
                    mManager.addFragment(f, false);
                    break;
                //...
                default:
                    throw new IllegalArgumentException("Unknown cmd: " + op.cmd);
            }
            if (!mReorderingAllowed && op.cmd != OP_ADD && f != null) {
                mManager.moveFragmentToExpectedState(f);
            }
        }
        if (!mReorderingAllowed) {
            // Added fragments are added at the end to comply with prior behavior.
            mManager.moveToState(mManager.mCurState, true);
        }
    }

    //FragmentManagerImpl
    public void addFragment(Fragment fragment, boolean moveToStateNow) {
        if (DEBUG) Log.v(TAG, "add: " + fragment);
        makeActive(fragment);
        if (!fragment.mDetached) {
            // 再这里它会检测 mAdded 中是否包含由这个 fragment 然后再进行添加操作
            // 这里就是崩溃的地方
            if (mAdded.contains(fragment)) {
                throw new IllegalStateException("Fragment already added: " + fragment);
            }
            synchronized (mAdded) {
                mAdded.add(fragment);
            }
            // 把 fragment 的 add 标记位置为 true
            fragment.mAdded = true;
            fragment.mRemoving = false;
            if (fragment.mView == null) {
                fragment.mHiddenChanged = false;
            }
            if (fragment.mHasMenu && fragment.mMenuVisible) {
                mNeedMenuInvalidate = true;
            }
            if (moveToStateNow) {
                moveToState(fragment);
            }
        }
    }
```

截至到上面的地方找到了崩溃的原因，就是在添加的时候其实已经存在了导致的，初步的解决办法是获取到 FragmentManagerImpl.mAdded 然后在添加之前主动的进行一次检查

```java
if (!fragment.isAdded() && !getSupportFragmentManager().getFragments().contains(fragment)){
    // 执行 add 操作 ...
    fragmentTransaction
            .hide(this.mCurrentFragment)
            .add(R.id.activity_main_fragment_container, fragment,
                                        this.mLastSelectFragmentTag + "")
            .show(fragment)
            .commitAllowingStateLoss();
}
```

但是经过测试发现上面的操作并没效果一样出现崩溃，究其原因其实是出在 commit 的机制上，上面的代码其实可以看出来 commit 的时候使用了 mHost.getHandler().post 来执行提交