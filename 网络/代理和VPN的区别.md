在真正的部署内网穿透用的 vpn 之前一直理解就是翻墙用的代理，然而实际使用了 vpn 的时候却发现两者并不能混为一谈。

参考卡巴斯基的这一篇文章————[VPN 与代理服务器：两者有什么区别，您应该使用哪个?](https://www.kaspersky.com.cn/resource-center/preemptive-safety/vpn-vs-proxy-server)

以及了解了一些其他资料以后可以大概总结以下几点：

- 工作的级别不一样

    一般来说的代理可以分为四层代理（tcp代理）、七层代理（http代理）、五层代理（socks代理），而vpn工作在第三层。

- 适用范围不同

    HTTP 代理很明显就是基于 web 设计的代理，通常用在浏览器或者其他基于HTTP 协议的地方，最明显的就是当使用 http 代理的时候即使给终端设置了代理，ping 一些敏感网站也是不通的，因为 ping 使用的 icmp 协议。
    SOCKS 代理比 http 代理适用性要宽泛一些，不仅网站，也可用于访问文件共享网站（FTP）、视频串流服务或在线游戏等
    VPN 因为VPN 更加底层因此它能接管几乎所有流量，VPN 会重定向所有流量。
    一个比较典型的就是 vpn 在用作内网穿透的时候可以直接在外部网络ping一个内网的ip。

- 安全性

    一个需要说明的是无论http还是socks在协议层面都没有对流量做加密，目前的普遍做法是由用户自己来对数据加密，然后再通过代理服务器发送出去。
    VPN 则不同，它可以对流量进行加密。

总结来说就是VPN是在操作系统级别上工作的，可以对整个设备上的所有应用程序进行加密和连接，可以确保所有流量都通过VPN通道传输。而代理则是对特定应用程序或浏览器有效，而不会影响其他网络连接。 比如一般使用代理时需要在网络设置中配置自动代理配置或者http、socks代理等，另外一个比较明显的例子就是在命令行中如果想要curl google，需要 curl -x http://127.0.0.1:1080 google.com 或者手动 export http_proxy=http://127.0.0.1:1080 等等，但是vpn则不同， vpn 工作在操作系统级别，一般vpn会修改系统的路由表，使得所有流量都通过VPN通道传输，而不管是curl还是浏览器均不再需要额外的配置。

2023-02-28 再次更新

通过国内所说的 vpn 即为fq代理，之所以有此的原因之一是因为 vpn 技术要比代理技术出现的早的多，同时 vpn 某些程度上也能实现代理上网的功能，最早的fq兴起的时候使用的很多fq软件都是基于vpn技术做的，比如 openVPN 等，再后来因为 vpn 的特征过于明显（对于墙来说vpn属于被加密的小众流量，而小众就意味着容易被识别），因此慢慢的 shadowsocks 开始兴起（基于 socks5 协议实现的专用fq代理协议），但是也很快大概是15年前后 ss 也被大面积封锁，目前针对 ss 的流量识别已经特别精准，因此后来又迭代出了 ssr 以及后续版本在 ss 的基础上增加了一些数据的混淆方式，但随着墙的技术发展也容易被识别；后来又新兴了 vmess 加密协议（即 V2Ray 的原创加密协议，根据最新消息 vmess 协议也容易被识别） trojan 协议等等

再次更新

关于现在的代理软件：

实际上现在的代理软件已经涉及到了一些vpn技术了，例如著名的 clash for mac 和 xray 都已经支持全局模式，所谓全局模式就是在本地开了一个虚拟网卡，然后通过修改系统路由的方式把产生的所有流量都路由到其中，然后这个虚拟网卡会把流量导入到本地的某个tcp或者udp端口中，此时流量就进入了代理软件，然后就可以根据这些流量进行分析是否需要代理，如果需要代理的流量会做进一步的加密再通过公网发送到上游的代理服务器中。（本身代理来说是不涉及到加密的，只是为了对抗防火墙代理软件都会对代理的流量进行加密）。

vpn的相同支持是也会在本地创建一个虚拟网卡，而vpn不同之处在于，这个虚拟网卡只会处理一些特定网段的流量（当然也可以处理全部流量），在多个不同的主机上运行vpn软件以后，理论上来说无论他们是不是在相同的网络中，这些主机就已经在一个相同的虚拟网络中了。那么这些不同的主机就可以使用虚拟网卡（IP）来进行通讯（当然实际的通讯过程也是通过已有的物理网络来进行的）。此时就能实现一个功能A机器可以把特定网段的流量直接转发到另外一个机器上，此时使用的是 NAT， 而不是代理技术。它不关心具体的应用层协议，无论是 ssh、http、ftp 、icmp等等都可以被转发。