macOS平台采集扬声器音频的方案和Windows差别很大，Windows可以通过系统的API直接采集扬声器音频。但是macOS平台则需要开发一款虚拟声卡驱动程序，可以参考 BlackHole: Virtual Audio Driver​github.com/ExistentialAudio/BlackHole大致的流程介绍一下，具体的原理自己查阅一下。通过虚拟声卡驱动，可以模拟出一个虚拟的音频输出设备和对应的音频输入设备，这里以BlackHole 2ch为例。如果想采集扬声器音频，则首先需要将系统默认的音频输出设备设置为BlackHole 2ch，然后就可以通过采集BlackHole 2ch音频输入设备来采集扬声器的音频了（注意这里是音频输入设备）。这里有个核心问题需要解决，因为是将虚拟的音频输出设备设置为系统默认的音频输出设备，那么系统播放的音频是无法真正的播出声音来的。要解决这个问题，就需要将采集到的音频写入到真实的物理音频输出设备中进行播放（系统内置的扬声器或者蓝牙耳机都是可以的）。其余的一些小细节也蛮多了，例如播放的过程中切换声卡（蓝牙耳机断开/连接）等，这块属于常规问题，慢慢优化即可。



另外一种简单点的方案就是，使用现有的虚拟声卡设备 如  BlackHole， 然后通过创建多输出设备的形式，把声音同时输出在扬声器和虚拟声卡上，然后直接在虚拟声卡上面进行录制，此时要注意的是 录制虚拟声卡时是录制的它的输入（相当于是它的麦克风），因此一定要有麦克风权限！。