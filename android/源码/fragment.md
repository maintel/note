# 当 add fragment 然后进行commitAllowingStateLoss 时的操作

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

```java
    public boolean execPendingActions() {
        ensureExecReady(true);

        boolean didSomething = false;
        // 通过循环把所有需要执行的操作添加到 mTmpRecords 中
        while (generateOpsForPendingActions(mTmpRecords, mTmpIsPop)) {
            mExecutingActions = true;
            try {
                // 去除重复的操作 然后执行
                removeRedundantOperationsAndExecute (mTmpRecords, mTmpIsPop);
            } finally {
                cleanupExec();
            }
            didSomething = true;
        }

        doPendingDeferredStart();
        burpActive();

        return didSomething;
    }
```

FragmentManagerImpl.removeRedundantOperationsAndExecute 方法会删除冗余的操作，然后再执行，它会对一些相似的操作进行合并，

```java
    private void removeRedundantOperationsAndExecute(ArrayList<BackStackRecord> records,
            ArrayList<Boolean> isRecordPop) {
         //...
        final int numRecords = records.size();
        int startIndex = 0;
        for (int recordNum = 0; recordNum < numRecords; recordNum++) {
            final boolean canReorder = records.get(recordNum).mReorderingAllowed;
            if (!canReorder) {
                // 执行之前的事务
                if (startIndex != recordNum) {
                    executeOpsTogether(records, isRecordPop, startIndex, recordNum);
                }
                // 所有不允许重新排序的操作，或者是 add 操作 放在一起执行
                int reorderingEnd = recordNum + 1;
                if (isRecordPop.get(recordNum)) {
                    while (reorderingEnd < numRecords
                            && isRecordPop.get(reorderingEnd)
                            && !records.get(reorderingEnd).mReorderingAllowed) {
                        reorderingEnd++;
                    }
                }
                //一起执行操作
                executeOpsTogether(records, isRecordPop, recordNum, reorderingEnd);
                startIndex = reorderingEnd;
                recordNum = reorderingEnd - 1;
            }
        }
        if (startIndex != numRecords) {
            executeOpsTogether(records, isRecordPop, startIndex, numRecords);
        }
    }
```

removeRedundantOperationsAndExecute 对所有的事务进行了重新处理以后调用了 executeOpsTogether 方法：

```java
   private void executeOpsTogether(ArrayList<BackStackRecord> records,
            ArrayList<Boolean> isRecordPop, int startIndex, int endIndex) {
        final boolean allowReordering = records.get(startIndex).mReorderingAllowed;
        boolean addToBackStack = false;
        if (mTmpAddedFragments == null) {
            mTmpAddedFragments = new ArrayList<>();
        } else {
            mTmpAddedFragments.clear();
        }
        mTmpAddedFragments.addAll(mAdded);
        // 确定当前活动的主导航 frgament
        Fragment oldPrimaryNav = getPrimaryNavigationFragment();
        for (int recordNum = startIndex; recordNum < endIndex; recordNum++) {
            final BackStackRecord record = records.get(recordNum);
            final boolean isPop = isRecordPop.get(recordNum);
            if (!isPop) {
                oldPrimaryNav = record.expandOps(mTmpAddedFragments, oldPrimaryNav);
            } else {
                oldPrimaryNav = record.trackAddedFragmentsInPop(mTmpAddedFragments, oldPrimaryNav);
            }
            addToBackStack = addToBackStack || record.mAddToBackStack;
        }
        mTmpAddedFragments.clear();

        if (!allowReordering) {
        // 如果不允许重新排序，当添加时会执行这一步，进行视图转换
            FragmentTransition.startTransitions(this, records, isRecordPop, startIndex, endIndex,
                    false);
        }
        executeOps(records, isRecordPop, startIndex, endIndex);

        int postponeIndex = endIndex;
        if (allowReordering) {
            ArraySet<Fragment> addedFragments = new ArraySet<>();
            addAddedFragments(addedFragments);
            postponeIndex = postponePostponableTransactions(records, isRecordPop,
                    startIndex, endIndex, addedFragments);
            makeRemovedFragmentsInvisible(addedFragments);
        }

        if (postponeIndex != startIndex && allowReordering) {
            // need to run something now
            FragmentTransition.startTransitions(this, records, isRecordPop, startIndex,
                    postponeIndex, true);
            moveToState(mCurState, true);
        }

        for (int recordNum = startIndex; recordNum < endIndex; recordNum++) {
            final BackStackRecord record = records.get(recordNum);
            final boolean isPop = isRecordPop.get(recordNum);
            if (isPop && record.mIndex >= 0) {
                freeBackStackIndex(record.mIndex);
                record.mIndex = -1;
            }
            record.runOnCommitRunnables();
        }
        if (addToBackStack) {
            reportBackStackChanged();
        }
    }
```

FragmentTransition.startTransitions 进行一系列的调用会调用到 FragmentTransition.addToFirstInLastOut 方法，这个方法用来检查命令，并且给 fragment 容器设置进出的标记，最终会调用 `manager.moveToState(fragment, Fragment.CREATED, 0, 0, false);`

```java
              // 在初始的时候 fragment.mState 为 0（INITIALIZING）
              // manager.mCurState 为 2（ACTIVITY_CREATED）
              // 这一步主要是为了防止出现重复创建 或者出现 activity 未创建的情况
            if (fragment.mState < Fragment.CREATED && manager.mCurState >= Fragment.CREATED
                    && !transaction.mReorderingAllowed) {
                manager.makeActive(fragment);
                manager.moveToState(fragment, Fragment.CREATED, 0, 0, false);
            }
```

moveToState 方法会触发很多回调，整个 fragment 生命周期中的回调都是通过它来触发的。

```java
    void moveToState(Fragment f, int newState, int transit, int transitionStyle,
            boolean keepActive) {
            //...
       switch (f.mState) {
                case Fragment.INITIALIZING:
                    if (newState > Fragment.INITIALIZING) {
                       //...
                       // 触发一些回调等
                        dispatchOnFragmentPreAttached(f, mHost.getContext(), false);
                        f.mCalled = false;
                        f.onAttach(mHost.getContext());
                        if (!f.mCalled) {
                            throw new SuperNotCalledException("Fragment " + f
                                    + " did not call through to super.onAttach()");
                        }
                        if (f.mParentFragment == null) {
                            mHost.onAttachFragment(f);
                        } else {
                            f.mParentFragment.onAttachFragment(f);
                        }
                        dispatchOnFragmentAttached(f, mHost.getContext(), false);

                        if (!f.mRetaining) {
                            dispatchOnFragmentPreCreated(f, f.mSavedFragmentState, false);
                            // 这里最终会触发 fragment 的onCreate 方法
                            f.performCreate(f.mSavedFragmentState);
                            dispatchOnFragmentCreated(f, f.mSavedFragmentState, false);
                        } else {
                            f.restoreChildFragmentState(f.mSavedFragmentState);
                            f.mState = Fragment.CREATED;
                        }
                        f.mRetaining = false;
                    }
                    //create
                    case Fragment.CREATED:
                    // This is outside the if statement below on purpose; we want this to run
                    // even if we do a moveToState from CREATED => *, CREATED => CREATED, and
                    // * => CREATED as part of the case fallthrough above.
                    ensureInflatedFragmentView(f);

                    if (newState > Fragment.CREATED) {
                        if (DEBUG) Log.v(TAG, "moveto ACTIVITY_CREATED: " + f);
                        if (!f.mFromLayout) {
                            ViewGroup container = null;
                            if (f.mContainerId != 0) {
                                if (f.mContainerId == View.NO_ID) {
                                    throwException(new IllegalArgumentException(
                                            "Cannot create fragment "
                                                    + f
                                                    + " for a container view with no id"));
                                }
                                container = (ViewGroup) mContainer.onFindViewById(f.mContainerId);
                                if (container == null && !f.mRestored) {
                                    String resName;
                                    try {
                                        resName = f.getResources().getResourceName(f.mContainerId);
                                    } catch (NotFoundException e) {
                                        resName = "unknown";
                                    }
                                    throwException(new IllegalArgumentException(
                                            "No view found for id 0x"
                                            + Integer.toHexString(f.mContainerId) + " ("
                                            + resName
                                            + ") for fragment " + f));
                                }
                            }
                            // 这里会回调 fragment 的 createView 等方法
                            f.mContainer = container;
                            f.mView = f.performCreateView(f.performGetLayoutInflater(
                                    f.mSavedFragmentState), container, f.mSavedFragmentState);
                            if (f.mView != null) {
                                f.mInnerView = f.mView;
                                f.mView.setSaveFromParentEnabled(false);
                                if (container != null) {
                                    container.addView(f.mView);
                                }
                                if (f.mHidden) {
                                    f.mView.setVisibility(View.GONE);
                                }
                                f.onViewCreated(f.mView, f.mSavedFragmentState);
                                dispatchOnFragmentViewCreated(f, f.mView, f.mSavedFragmentState,
                                        false);
                                // Only animate the view if it is visible. This is done after
                                // dispatchOnFragmentViewCreated in case visibility is changed
                                f.mIsNewlyAdded = (f.mView.getVisibility() == View.VISIBLE)
                                        && f.mContainer != null;
                            } else {
                                f.mInnerView = null;
                            }
                        }

                        f.performActivityCreated(f.mSavedFragmentState);
                        dispatchOnFragmentActivityCreated(f, f.mSavedFragmentState, false);
                        if (f.mView != null) {
                            f.restoreViewState(f.mSavedFragmentState);
                        }
                        f.mSavedFragmentState = null;
                    }
                    // fall through
                case Fragment.ACTIVITY_CREATED:
                    if (newState > Fragment.ACTIVITY_CREATED) {
                        f.mState = Fragment.STOPPED;
                    }
                    // fall through
                case Fragment.STOPPED:
                    if (newState > Fragment.STOPPED) {
                        if (DEBUG) Log.v(TAG, "moveto STARTED: " + f);
                        f.performStart();
                        dispatchOnFragmentStarted(f, false);
                    }
                    // fall through
                case Fragment.STARTED:
                    if (newState > Fragment.STARTED) {
                        if (DEBUG) Log.v(TAG, "moveto RESUMED: " + f);
                        f.performResume();
                        dispatchOnFragmentResumed(f, false);
                        f.mSavedFragmentState = null;
                        f.mSavedViewState = null;
                    }
        }
        
         if (f.mState != newState) {
            Log.w(TAG, "moveToState: Fragment state for " + f + " not updated inline; "
                    + "expected state " + newState + " found " + f.mState);
            // 设置 state
            f.mState = newState;
        }
    }
```

这里的回调过程比较复杂，当第一次的时候 fragment.mState 为 0，这个时候会触发 fragment 的 create 方法，调用完以后 fragment.mState 为 1，然后代码继续执行FragmentManagerImpl.executeOpsTogether 方法接着调用了 `executeOps(records, isRecordPop, startIndex, endIndex);`，然后继续调用了 BackStackRecord.executeOps 方法，

```java
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
                    // 这里执行了 add 操作，
                    mManager.addFragment(f, false);
                    break;
                    //...
        }
        if (!mReorderingAllowed) {
            // Added fragments are added at the end to comply with prior behavior.
            mManager.moveToState(mManager.mCurState, true);
        }
    }
```

`mManager.addFragment(f, false);` 方法中执行了真正的 add 操作，

```java
    public void addFragment(Fragment fragment, boolean moveToStateNow) {
        if (DEBUG) Log.v(TAG, "add: " + fragment);
        makeActive(fragment);
        if (!fragment.mDetached) {
            if (mAdded.contains(fragment)) {
                throw new IllegalStateException("Fragment already added: " + fragment);
            }
            synchronized (mAdded) {
                mAdded.add(fragment);
            }
            // 设置标记位
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
然后继续调用了这个方法执行完了以后它继续调用了`mManager.moveToState(mManager.mCurState, true);` 方法，这个方法最终经过一系列的调用：moveFragmentToExpectedState -> moveToState(f, nextState, f.getNextTransition(), f.getNextTransitionStyle(), false);又调回了上面的 moveToState 方法，但是此时 fragment.mState 为 1，nextState 为2，这个时候就会触发 fragment 的 onViewCreate 等方法，然后接下来就是根据 fragmentActivity 回调导致的 fragment 的 onRsume 等方法的调用。

在 fragment.mState 为 1，nextState 为2 是一个很巧妙的设计，当 fragmentActivity 被创建的时候会把 fragmentManager.mCurState 设置为 ACTIVITY_CREATED == 2，当 fragment 被 create 的时候 会把标记位设置为 CREATED == 1，这个时候第二次 moveToState 就保证了需要在 activity 被创建以后 fragment 才能被创建。

