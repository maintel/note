<!-- TOC -->

- [slingTop模式](#slingtop模式)
- [slingTask模式](#slingtask模式)
- [slingInstance模式](#slinginstance模式)

<!-- /TOC -->

## slingTop模式

位于栈顶的时候不会重复创建，当没有在栈顶的时候和standard一样。

当位于栈顶的时候，不会重复创建，但是生命周期执行顺序 onPause--onNewIntent--onResume.

## slingTask模式

- 如果不指定taskAffinity属性，则会一直在同一个任务栈中

当前任务栈中如果有此，则不会重复创建。会把它之上的activity出栈，并移至栈顶。

- 如果指定了taskAffinity属性，则会在一个新的任务栈中创建，而且通过此activity启动的activity也会在这个新的任务栈中。

但是此时如果使用startActivityForResult启动，即使设置了taskAffinity属性，也不会创建新的任务栈！！！但是在其他activity中再启动这个activity，会创建新的任务栈，而且此时会存在两个activity，分别存在于两个activity中。

如下：有三个Activity分别为MainActivity,SecondActivity,ThirdActivity,其中MainActivity和ThirdActivity为普通启动模式，SecondActivity的启动方式如下：

![SecondActivity启动方式](http://orzoelfvh.bkt.clouddn.com/secondActivity%E7%9A%84xml.png?attname=&e=1500479686&token=cs2nCfx72Y7hW0_NpFYzb3Jab90IJWraRtphMd-q:rnhC9gsXHjCUL0L1aNSh-XGPxJ0)

在MainActivity中启动SecondActivity如下：

```java
                Intent intent = new Intent(MainActivity.this, SecondActivity.class);
                startActivityForResult(intent, 1002);
```

在SecondActivity普通启动ThirdActivity，再在ThirdActivity中普通启动SecondActivity，此时：

当从MainActivity启动SecondActivity时，任务栈如下：

![M-secondActivity任务栈](http://orzoelfvh.bkt.clouddn.com/startActivityForResult%E5%90%AF%E5%8A%A81.png?attname=&e=1500479686&token=cs2nCfx72Y7hW0_NpFYzb3Jab90IJWraRtphMd-q:aQbb8T-hh6ssHWGHomgEYxofNCQ)

而当执行SecondAcitivyt----ThirdActivity---SecondActivity时，任务栈如下：

![M-S-T-S](http://orzoelfvh.bkt.clouddn.com/startActivityForResult%E5%90%AF%E5%8A%A82.png?attname=&e=1500479686&token=cs2nCfx72Y7hW0_NpFYzb3Jab90IJWraRtphMd-q:HRac2_YxoTCifBMuljrfc47LOUE)

如果原本就在栈顶，则生命周期执行顺序 onPause--onNewIntent--onResume.

如果原本不在栈顶，则生命周期顺序 onNewIntent--onRestart--onStart--onResume.

## slingInstance模式


官方的说法是：

* 以singleInstance模式启动的Activity具有全局唯一性，即整个系统中只会存在一个这样的实例
    
* slingInstance模式启动的activity会独占一个任务栈。
    
* 被singleInstance模式的Activity开启的其他activity，会在新的任务栈中启动，但不一定开启新的任务栈，也可能在已有的一个任务栈中开启

实际验证如果以startActivityForResult启动一个 slingInstance模式的activity,则会和启动它的那个activity同一个任务栈，而此时这个activity再启动其他的activity会使这个activity在一个新的任务栈中，并且是被以slingTask模式启动。

如下：

有三个Activity分别为MainActivity,SecondActivity,ThirdActivity,其中MainActivity和ThirdActivity为普通启动模式，SecondActivity为slingInstance模式；

- 1、此时 MainActivity 通过 startActivityForResult 启动 SecondActivity 结果如下：

        Running activities (most recent first):
          TaskRecord{2a04f0ca #58 A=maintel.activitylaunchmode U=0 sz=2}
            Run #1: ActivityRecord{3beb0d4 u0 maintel.activitylaunchmode/.SecondActivity t58}
            Run #0: ActivityRecord{19d20c u0 maintel.activitylaunchmode/.MainActivity t58}
        Running activities (most recent first):
          TaskRecord{5d30fb #29 A=com.android.launcher3 U=0 sz=1}
            Run #0: ActivityRecord{d0dd3bb u0 com.android.launcher3/.Launcher t29}

可以看到 MainActivity 和 SecondActivity 在同一个任务栈中；

- 2、此时再启动 ThirdActivity 然后从 ThirdActivity  可以看到任务栈如下：

        Running activities (most recent first):
          TaskRecord{204dcae0 #62 A=maintel.activitylaunchmode U=0 sz=2}
            Run #2: ActivityRecord{29af2926 u0 maintel.activitylaunchmode/.SecondActivity t62}
          TaskRecord{3e2fd199 #63 A=maintel.activitylaunchmode U=0 sz=1}
            Run #1: ActivityRecord{3adb70ac u0 maintel.activitylaunchmode/.ThirdActivity t63}
          TaskRecord{204dcae0 #62 A=maintel.activitylaunchmode U=0 sz=2}
            Run #0: ActivityRecord{34495477 u0 maintel.activitylaunchmode/.MainActivity t62}
        Running activities (most recent first):
          TaskRecord{5d30fb #29 A=com.android.launcher3 U=0 sz=1}
            Run #0: ActivityRecord{d0dd3bb u0 com.android.launcher3/.Launcher t29}

可以看到 ThirdActivity 在一个新的任务栈中，而 MainActivity 和 SecondActivity 在同一个任务栈中。

- 3、然后从 ThirdActivity 中再启动 SecondActivity，然后再次启动 ThirdActivity，可以看到：

        Running activities (most recent first):
          TaskRecord{1b8682ef #65 A=maintel.activitylaunchmode U=0 sz=1}
            Run #2: ActivityRecord{14ac7270 u0 maintel.activitylaunchmode/.ThirdActivity t65}
          TaskRecord{2804c1fc #64 A=maintel.activitylaunchmode U=0 sz=2}
            Run #1: ActivityRecord{838bca u0 maintel.activitylaunchmode/.SecondActivity t64}
            Run #0: ActivityRecord{2586ef4b u0 maintel.activitylaunchmode/.MainActivity t64}
        Running activities (most recent first):
          TaskRecord{5d30fb #29 A=com.android.launcher3 U=0 sz=1}
            Run #0: ActivityRecord{d0dd3bb u0 com.android.launcher3/.Launcher t29}

可以看到 ThirdActivity 在任务栈中只有一个，因此可以知道此时 ThirdActivity 是通过 slingTask模式启动的。

- 4、如果此时再从 ThirdActivity 中启动 SecondActivity ，此时如果按返回键，会回到 MainActivity 中，再返回会回退到 ThirdActivity 中，再次返回退出应用。

**同样的，如果以 startActivity**启动 SecondActivity 则会有不同的情况

还是同样的 activity 同样的步骤：

- 1、此时 MainActivity 通过 startActivity 启动 SecondActivity 结果如下：

        Running activities (most recent first):
          TaskRecord{3e330aa0 #67 A=maintel.activitylaunchmode U=0 sz=1}
            Run #1: ActivityRecord{13ca517 u0 maintel.activitylaunchmode/.SecondActivity t67}
          TaskRecord{e63ecb1 #66 A=maintel.activitylaunchmode U=0 sz=1}
            Run #0: ActivityRecord{2ec34a09 u0 maintel.activitylaunchmode/.MainActivity t66}
        Running activities (most recent first):
          TaskRecord{5d30fb #29 A=com.android.launcher3 U=0 sz=1}
            Run #0: ActivityRecord{d0dd3bb u0 com.android.launcher3/.Launcher t29}

可以看到 SecondActivity 和 MainActivity 不在同一个任务栈中了已经。

- 2、此时再启动 ThirdActivity 然后从 ThirdActivity  可以看到任务栈如下：

          Running activities (most recent first):
            TaskRecord{e63ecb1 #66 A=maintel.activitylaunchmode U=0 sz=2}
              Run #2: ActivityRecord{20b87659 u0 maintel.activitylaunchmode/.ThirdActivity t66}
            TaskRecord{3e330aa0 #67 A=maintel.activitylaunchmode U=0 sz=1}
              Run #1: ActivityRecord{13ca517 u0 maintel.activitylaunchmode/.SecondActivity t67}
            TaskRecord{e63ecb1 #66 A=maintel.activitylaunchmode U=0 sz=2}
              Run #0: ActivityRecord{2ec34a09 u0 maintel.activitylaunchmode/.MainActivity t66}
          Running activities (most recent first):
            TaskRecord{5d30fb #29 A=com.android.launcher3 U=0 sz=1}
              Run #0: ActivityRecord{d0dd3bb u0 com.android.launcher3/.Launcher t29}

可以看到 MainActivity 和 ThirdActivity 在同一个任务栈中，而 SecondActivity 在单独的任务栈中

- 3、然后从 ThirdActivity 中再启动 SecondActivity，然后再次启动 ThirdActivity，可以看到：

        Running activities (most recent first):
          TaskRecord{e63ecb1 #66 A=maintel.activitylaunchmode U=0 sz=3}
            Run #3: ActivityRecord{3687d1ef u0 maintel.activitylaunchmode/.ThirdActivity t66}
          TaskRecord{3e330aa0 #67 A=maintel.activitylaunchmode U=0 sz=1}
            Run #2: ActivityRecord{13ca517 u0 maintel.activitylaunchmode/.SecondActivity t67}
          TaskRecord{e63ecb1 #66 A=maintel.activitylaunchmode U=0 sz=3}
            Run #1: ActivityRecord{20b87659 u0 maintel.activitylaunchmode/.ThirdActivity t66}
            Run #0: ActivityRecord{2ec34a09 u0 maintel.activitylaunchmode/.MainActivity t66}
        Running activities (most recent first):
          TaskRecord{5d30fb #29 A=com.android.launcher3 U=0 sz=1}
            Run #0: ActivityRecord{d0dd3bb u0 com.android.launcher3/.Launcher t29}

可以看到t66任务栈中存在一个 MainActivity 以及两个 ThirdActivity ， SecondActivity 同样在单独的任务栈中

- 4、如果此时再从 ThirdActivity 中启动 SecondActivity ，此时如果按返回键，会回到 ThirdActivity 中，再返回还是 ThirdActivity 中，再次返回是 MainActivity 再次返回退出应用，因为如第三步所说 ThirdActivity 在任务栈中存在了两个。
