go 可以使用 go build -tags 命令编译成指定平台的可执行文件，例如以下命令:

    CGO_ENABLED=1 GOARCH=arm64 GOOS=darwin CC="clang $CFLAGS" go build -tags macosx -ldflags=-w -trimpath -v -o "libvpnarm.a" -buildmode c-archive

上面的命令解析：

其中 GOARCH 代表了cpu指令集， GOOS 指定平台

GOOS的有效值：android，darwin，dragonfly，freebsd，js，linux，netbsd，openbsd，plan9，solaris，windows。

darwin代表Mac OS和iOS

GOARCH的有效值：arm，arm64、386，amd64，ppc64，ppc64le，mpis，mpisle，mps64，mips64le，s390x，wasm。

386表示32位Intel兼容CPU，而amd64是64位Intel兼容CPU

并不是所有的组合都有效果。

go build -tags macosx 表示编译成 macos 。

-o xxx.a 静态库的名字

生成的产物有 libvpnarm.a 和 libvpnarm.h。

如果想让go中暴露出一些方法供使用方调用则需要在相应的函数中加上注释 //export 如下

```go
//export initVpn
func initVpn(params string) int {
	return 1
}
```

在编译成对应平台时需要注意指令集的问题

# mac

脚本

    export CFLAGS="-mmacosx-version-min=10.14 -isysroot "$(xcrun -sdk macosx --show-sdk-path) 
    CGO_LDFLAGS="-mmacosx-version-min=10.14 -isysroot "$(xcrun -sdk macosx --show-sdk-path)  
    CGO_ENABLED=1 GOARCH=amd64 GOOS=darwin CC="clang $CFLAGS" go build -tags macosx -ldflags=-w -trimpath -v -o "libvpn86.a" -buildmode c-archive

    export CFLAGS="-mmacosx-version-min=10.14 -isysroot "$(xcrun -sdk macosx --show-sdk-path) 
    CGO_LDFLAGS="-mmacosx-version-min=10.14 -isysroot "$(xcrun -sdk macosx --show-sdk-path)  
    CGO_ENABLED=1 GOARCH=arm64 GOOS=darwin CC="clang $CFLAGS" go build -tags macosx -ldflags=-w -trimpath -v -o "libvpnarm.a" -buildmode c-archive

    lipo -create libvpn86.a libvpnarm.a -output libvpnall.a
    lipo -info libvpnall.a

分别生成 x86 和 arm 指令集的静态库，然后再把两个静态库合并成一个。

# windows

    # 编译动态库
    SET CGO_ENABLED=1 CC=x86_64-w64-mingw32-gcc CXX=x86_64-w64-mingw32-g++ GOOS=windows GOARCH=amd64
    go build -o libvpn64.dll -buildmode=c-shared vpn.go

    # 编译 exe
    SET GOOS=windows GOARCH=amd64
    go build -trimpath -o build/windows-amd64/core.exe -ldflags "-X main.Build=1.0.0 -H windowsgui" main.go