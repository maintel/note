
[官方文档](https://developer.apple.com/documentation/networkextension/packet_tunnel_provider)

# 前言

最近有一个需求是开发一个可以在手机端链接公司内网的VPN工具。经过技术选型决定使用 [nebula](https://github.com/slackhq/nebula) 来做这件事情。

首先要搞清楚 [代理和 VPN 的区别](../网络/%E4%BB%A3%E7%90%86%E5%92%8CVPN%E7%9A%84%E5%8C%BA%E5%88%AB.md)。

总结一下 iOS 开发 VPN 的理论，所谓的 vpn 也好，代理也好实际上就是怎么玩转儿系统网卡发出的流量，让它们能够按照我们想要的路径去转发。我这边主要是为了实现内网穿透，以便可以在公司外访问到公司内网。

苹果给开发者提供了 NetworkExtension 可以是开发者介入到系统的网络数据处理中，然后当成功的启动了网络扩展以后对数据的处理方式有很多种，

- 系统提供的 http 代理能力

这里就是通常所说的http或者socks代理，它基于系统提供的 API（NEProxySettings）， 只需要我们知道代理服务器的ip和端口即可简单的设置代理服务，同时它还提供了基于 pac 的代理配置，这时候只要有一个可以正常访问的 pac 文件地址配置即可。

此时系统就会自动的把想要的流量发送到代理服务器中。

- 直接从网卡读取数据

这种方式支持直接从网卡中读取数据，操作方式更为底层但使用起来也比较麻烦，不过好在已经有很多人已经造好了轮子比如本次开发 VPN 中使用的 nebula


下面正式开始。

# 首先就是创建一个 NetworkExtension 

这一步可以直接参考网络中已有的教程，如果要给现有的应用添加，可能需要重新配置一下证书什么的。

id 的命名尽量宿主的id+xxxx 样式的，容易识别。

然后就是打包的时候要注意扩展选用的证书要和宿主app的证书一致，否则打包不成功。

# NETunnelProviderManager

NETunnelProviderManager 用来创建和管理 vpn 的配置。每次保存了一个 manager 的配置以后可以在设置中看到一个 vpn 配置的链接，简单的代码如下：

```swift
    class func save(oldManager:NETunnelProviderManager?,callback: @escaping (NETunnelProviderManager?,Error?) -> ()){
        var manager:NETunnelProviderManager?
        if(oldManager != nil){
            oldManager!.loadFromPreferences { error in
                if(error != nil){
                    return callback(nil,error)
                }
                manager = oldManager!
            }
        }else {
            manager = NETunnelProviderManager()
        }
        
        let proto = manager!.protocolConfiguration as? NETunnelProviderProtocol ?? NETunnelProviderProtocol()
        proto.providerBundleIdentifier = "id"
        proto.providerConfiguration = ["config":"xxxx"]
        proto.serverAddress = "xxxx"   // 并不是必须的

        manager!.protocolConfiguration = proto
        manager!.localizedDescription = "Name"
        manager!.isEnabled = true
        manager!.saveToPreferences{ err in
            return callback(manager,err)
        }
    }
```

这里理论上我们可以把所有配置都保存在   proto.providerConfiguration 中，这样的话即使在不启动 app 的情况下直接在设置中打开 vpn 就能直接使用，当然也可以不做任何配置具体的处理逻辑都写在后续的 NEPacketTunnelProvider 实现类中（这种情况下必须启动 app 才能使用）。

需要注意的是 NETunnelProviderManager 的保存可以放在 NetworkExtension 中实现，也可以直接在宿主中，如果在宿主中做的话一定要设置 ` proto.providerBundleIdentifier = "扩展的id"`。

然后就是启动了。

当成功的获取到 NETunnelProviderManager 以后就可以直接启动了，不过保险起见我们可以先设置 isEnabled 为 true，然后保存一下，接着重新load manager，再启动。

```swift
        manager.loadFromPreferences { error in
            manager.isEnabled = true
            manager.saveToPreferences { error in
                manager.loadFromPreferences { error in
                    do{
                        // 这里主要是注册了一个 NSNotification.Name.NEVPNStatusDidChange 监听，用来处理 vpn 状态成功链接以后再做后续操作
                        self.netUpdater?.registNotification(vpnItem: self.vpnItem!)  
                        self.netUpdater?.startFunc = {() -> Void in
                            // 监听到启动成功 则通过ipc通讯在网络扩展中启动相应的网络处理操作
                            return self.vpnRequest(command: "start", arguments: call.arguments, result: result)
                        }
                        try manager.connection.startVPNTunnel(options: ["expectStart": NSNumber(1)])
                    } catch {
                        print("启动tunnel失败 \(error)")
                        return result(-6)
                    }
                }
            }
        }
```

当 vpn 成功启动以后就可以通过 ipc 在  NetworkExtension 做一些后续的操作，（当然这一步要看具体的业务逻辑，如果仅仅是做http代理无需一些复杂的业务逻辑，则直接把一些数据参数写死 ，NetworkExtension 成功启动以后直接设置参数即可）

ipc 通讯的方法如下 
```swift

         let session = self.manager?.connection as? NETunnelProviderSession 
            do {
                try session.sendProviderMessage(xxx){data in 


                } catch {

                }
        
```

# NEPacketTunnelProvider

经过上面的步骤 vpn 此时已经成功启动了，但是仅仅启动了vpn并不能保证能够成功通讯，后续的网络数据处理更重要。

在 NetworkExtension 中实现一个 PacketTunnelProvider 继承 NEPacketTunnelProvider ，当上一步的 startVPNTunnel 被成功调用时 PacketTunnelProvider 的 startTunnel 也会被调用，

正如上面说保存的，这个类提供了一个 protocolConfiguration 变量它是一个 NETunnelProviderProtocol 对象，它里面就保存了之前保存的配置，根据业务逻辑可以直接从这里读取配置然后启动 vpn 处理后续逻辑。

不过我这边的逻辑不太一样我通过从 ipc 通讯传递过来的数据来启动 vpn 后续的逻辑处理，那么在 startTunnel 方法就直接返回。

重写 NEPacketTunnelProvider 的 handleAppMessage 方法，接收从宿主传递过来的信息即可。这部分代码就不贴了，看一下后续的 vpn 处理逻辑吧。


```swift
  private func start(
        ip:String,
        cert:String,
        completionHandler: @escaping (Error?) -> Void) {
            let proto = self.protocolConfiguration as! NETunnelProviderProtocol
            var config: Data
            var key: String
            
            
            
            let fileDescriptor = tunnelFileDescriptor
            if fileDescriptor == nil {
                return completionHandler(CallFailedError(message:"Unable to locate the tun file descriptor"))
            }
            // 拿到虚拟网卡的描述符
            let tunFD = Int(fileDescriptor!)
            
            // This is set to 127.0.0.1 because it has to be something..
            let tunnelNetworkSettings = NEPacketTunnelNetworkSettings(tunnelRemoteAddress: "127.0.0.1")
            var err: NSError?
            // 解析ip
            let ipNet =  Vpn_client_mobile.Vpn_client_mobileParseCIDR(ip, &err)
            if (err != nil) {
                return completionHandler(err!)
            }
            
            // 这里设置路由规则
            tunnelNetworkSettings.ipv4Settings = NEIPv4Settings(addresses: [ipNet!.ip], subnetMasks: [ipNet!.maskCIDR])
            var routes: [NEIPv4Route] = [NEIPv4Route(destinationAddress: ipNet!.network, subnetMask: ipNet!.maskCIDR)]
            // 配置内网穿透规则，简单来说就是配置那些网段的请求自动转发到虚拟网卡中。
            routes.append(NEIPv4Route(destinationAddress: "192.168.11.0", subnetMask: ipNet!.maskCIDR))
            tunnelNetworkSettings.ipv4Settings!.includedRoutes = routes
            tunnelNetworkSettings.mtu = 1300
      
            self.setTunnelNetworkSettings(tunnelNetworkSettings, completionHandler: {(error:Error?) in
                if (error != nil) {
                    return completionHandler(error!)
                }
                var err: NSError?
                self.nebula =  Vpn_client_mobile.Vpn_client_mobileNewNebula(cert, tunFD, &err)
                if err != nil {
                    return completionHandler(err!)
                }
                self.nebula!.start()
                self.startNetworkMonitor()
                if err != nil {
                    completionHandler(err)
                    return
                }
                completionHandler(nil)
            })  
        }
```

这里的 Vpn_client_mobile 是用 neubla 编译的 frameworks。它通过虚拟网卡描述符创建虚拟网卡，然后读取网卡数据并接管之后的链接。


以上就是VPN开发中最核心的部分，具体代码可以参考 [mobile_nebula](https://github.com/DefinedNet/mobile_nebula)
