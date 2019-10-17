# 获取机型

    adb shell getprop | grep ro.product.model

# adb shell

## 查看当前运行的activity，service信息等

    adb shell dumpsys activity ---查看ActvityManagerService 所有信息
    adb shell dumpsys activity activities----------查看Activity组件信息
    adb shell dumpsys activity services-----------查看Service组件信息
    adb shell dumpsys activity providers----------产看ContentProvider组件信息
    adb shell dumpsys activity broadcasts--------查看BraodcastReceiver信息
    adb shell dumpsys activity intents--------------查看Intent信息
    adb shell dumpsys activity processes---------查看进程信息

得到的信息很详细，可以使用以下命令来替换，比如只查看运行中activity任务栈的信息，执行以下命令

    adb shell dumpsys activity activities | sed -En -e '/Running activities/,/Run #0/p'

有时候会提示sed不是内部或者外部命令，可以先执行adb shell，然后执行adb shell后的命令即可。



## 查看当前应用的线程数


ps 查找当前 pid

cat /proc/pid/status

打印出来的信息中 threads 就是当前进程中包含的线程数