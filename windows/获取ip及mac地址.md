在 dart 中获取ip思路。

本身 dart 自身的  NetworkInterface.list 方法可以获取到ip地址，同时可以把回环ip等排除出去以后就可以可以了，但是要考虑到多网卡的情况，或者同时插着网线和连着wifi

此时我们需要找到哪一个才是主网卡，思路就是通过 route print 命令获取路由表，通过匹配路由表中 0.0.0.0 的路由的跳跃点数来确定哪个是主网卡，然后通过和 NetworkInterface 中的对应网卡匹配index，从而可以通过index拿到对应网卡的mac地址。

以下是代码

```dart

        var list = await NetworkInterface.list(
            includeLinkLocal: false,
            includeLoopback: false,
            type: InternetAddressType.IPv4);
        Map<String, int> ips = {};
        list.forEach((element) {
          ips[element.addresses[0].address] = element.index;
        });
        var processRes = await Process.run("route", ["print"]);
        if (processRes.stdout != null && processRes.stdout != "") {
            // 匹配出默认路由
          RegExp regExpIps = RegExp(
              r'^\s+0\.0\.0\.0\s+0\.0\.0\.0\s+\d+\.\d+\.\d+\.\d+\s+\d+\.\d+\.\d+\.\d+\s+\d+',
              multiLine: true);
          Iterable<Match> matchs = regExpIps.allMatches(processRes.stdout);
          String currentIp = "";
          int currentIndex = -1;
          // 找到最小跳点数，即默认网卡
          for (var element in matchs) {
            var ipRoute = element.group(0)?.trim().split(RegExp(r"\s+"));
            int index = int.parse(ipRoute![4]);
            if (currentIndex == -1 || index < currentIndex) {
              print(ipRoute);
              currentIndex = index;
              currentIp = ipRoute[3];
            }
          }
          int interfaceIndex = ips[currentIp]!;
          RegExp regExpMac = RegExp(
              "^\\s+${interfaceIndex}\\.\\.\\.(([0-9A-Fa-f]{2}\\s){5}[0-9A-Fa-f]{2})",
              multiLine: true);
          var interfaceMatch = regExpMac.firstMatch(processRes.stdout);
          ipMacs["ip"] = currentIp;
          ipMacs["mac"] = interfaceMatch
                  ?.group(0)
                  ?.trim()
                  .split("...")[1]
                  .replaceAll(" ", ":") ??
              "";
```