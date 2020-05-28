虽然 flutter 官方提供了混合开发解决方案，但是其存在着一些问题并没有解决，比如原生和Flutter页面叠加跳转由于Flutter Engine重复创建而导致内存暴增的问题、Flutter应用中全局变量在各独立页面不能共享的问题、iOS平台内存泄露的问题等等，目前官方在混合开发解决方案上并没有花太多的时间去改进优化。

目前国内对 flutter 研究和使用最多的厂商非咸鱼莫属，他们也提供了一套针对混编交互的解决方案 flutterBoots。

[官方介绍](https://mp.weixin.qq.com/s/v-wwruadJntX1n-YuMPC7g)

[项目地址](https://github.com/alibaba/flutter_boost)

