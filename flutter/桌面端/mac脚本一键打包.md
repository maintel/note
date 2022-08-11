经过一番查证，发现 mac 打包还是可以使用脚本一键完成的，具体流程如下：

# 打包命令

有几个关键的命令：

- flutter build   编译 flutter
- xcodebuild archive 启动xcode archive
- xcodebuild -exportArchive  导出 archvie 的文件
    这一步需要配置  需要配置 ExportOptions.plist, 
- xcrun altool -type osx --notarize-app  上传到公证服务器
- xcrun altool --notarization-info     查询公证结果

# 参考资料

[Mac开发-公证流程记录Notarization-附带脚本](https://blog.csdn.net/shengpeng3344/article/details/103369804)

[iOS 自动化打包--(手动运行xcodebuild命令)](https://blog.csdn.net/ioszhanghui/article/details/91046928)

[自定义公证流程](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution/customizing_the_notarization_workflow?preferredLanguage=occ)

[自定义打包流程](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution/customizing_the_notarization_workflow/customizing_the_xcode_archive_process)

# 打包脚本

```sh
# 以下是自动打包流程，包含了编译，archive，导出，签名，公证，生成升级文件等一系列步骤，目前不支持上传到 oss需要手动到 oss 后台操作
# 参考下面参数进行配置， 不配置则会取默认值，
# macos 自动打包脚本，支持设置 versionName， versionCode， 编译环境，服务器环境， 打包完成 versionName 自动+1，版本记录在 version.txt 中
# -vc versionCode
# -vn versionName
# -st 服务器接口环境 默认为 release
# -bt 编译环境      默认为 --release
# -clean 打包前clean一下工程

currentVersionName="1.0.1"
currentVersionCode=75

# 读取当前的版本号
while read line
    do
        k=${line%=*}
        v=${line#*=}
        if [ ${k} = "mac_version_name" ]; then
            currentVersionName=${line#*=}
        elif [ ${k} = "mac_version_code" ]; then
            currentVersionCode=${line#*=}
        fi
done < ../version.txt

echo "currentVersionName:   ${currentVersionName}"
echo "currentVersionCode:   ${currentVersionCode}"

newVersionCode=`expr ${currentVersionCode} + 1`
newVersionName=${currentVersionName}

buildType="--release"
serviceType="release"
clean="false"
customVersionName="false"

while [ -n "$1" ]
do
    case "$1" in
        -vc) newVersionCode="$2"
            shift ;;
        -vn) newVersionName="$2"
            customVersionName="true"
            shift ;;
        -st) serviceType="$2"
            shift ;;
        -bt) buildType="$2" 
            shift ;;
        -clean) clean="true"
            shift ;;
         *) echo "$1 is not an option"
            exit 1 ;;  # 发现未知参数，直接退出
    esac
    shift
done

echo "newVersionName:   ${newVersionName}"
echo "newVersionCode:   ${newVersionCode}"

if [ "${clean}" = "true" ]; then
    echo "flutter clean"
    flutter clean
    echo "flutter pub get"
    flutter pub get
fi

echo "flutter build macos ${buildType} --dart-define=SERVER_TYPE=${serviceType}  --build-name ${newVersionName} --build-number ${newVersionCode} --dart-define=VERSION_NAME=${newVersionName}  --dart-define=VERSION_CODE=${newVersionCode}"

workPath=`pwd`
archivePath="../build/macos"
exportPath="./app_temp/${newVersionName}_${newVersionCode}"
appPath="$exportPath/xxxx.app"
zipPath="$exportPath/${newVersionName}_${newVersionCode}.zip"
dmgPath="$exportPath/${newVersionName}_${newVersionCode}.dmg"

mkdir -p "$exportPath"

# 编译 flutter
flutter build macos ${buildType} --dart-define=SERVER_TYPE=${serviceType}  --build-name ${newVersionName} --build-number ${newVersionCode} --dart-define=VERSION_NAME=${newVersionName}  --dart-define=VERSION_CODE=${newVersionCode} &> "$exportPath/flutter build.log"

if [ $? -ne 0 ]; then
    echo "build failed"
    exit 1
else
    echo "build success"
fi


# archive 打包
xcodebuild archive -workspace Runner.xcworkspace -scheme Runner -configuration Release -archivePath ${archivePath} &> "$exportPath/Xcode archive.log"

if [ $? -ne 0 ]; then
    echo "[xcode] archive failed"
    exit 1
else
    echo "[xcode] archive success"
fi

sed -i "" "s/mac_version_name=${currentVersionName}/mac_version_name=${newVersionName}/" ../version.txt
sed -i "" "s/mac_version_code=${currentVersionCode}/mac_version_code=${newVersionCode}/" ../version.txt

# 导出 archive 并签名
/usr/bin/xcodebuild -exportArchive -archivePath "$archivePath.xcarchive" -exportOptionsPlist "$workPath/ExportOptions.plist" -exportPath "$exportPath" &> "$exportPath/Xcode export.log"


mkdir -p "$exportPath/xxx"
# 将应用程序的快捷方式拷贝到app下
cp 应用程序 "$exportPath/xxx"
mv -v "$appPath" "$exportPath/xxx"

# 因为公证服务不能直接接收app文件，所以先制作 dmg再公证
/usr/bin/hdiutil create -srcfolder "$exportPath/xxx" -format UDBZ "$dmgPath"

# 上传公证服务
xcrun altool -type osx --notarize-app --primary-bundle-id "com.xxxx" --username "xxxx@xxx.com" --password "xxxxxx" --file "$dmgPath" &> tmp

sleep 5
uuid=`cat tmp | grep -Eo '\w{8}-(\w{4}-){3}\w{12}$'`

if [ "$uuid" == "" ]; then
    echo "上传公证失败！！"
    exit 1
fi

echo "$uuid"

# 循环查询公正结果
while true; do
    echo "查询公正结果"
 
    xcrun altool --notarization-info ${uuid} --username "xxxx@xxx.com" --password "xxxxxx" &> tmp
    r=`cat tmp`
    t=`echo "$r" | grep "success"`
    f=`echo "$r" | grep "invalid"`
    if [[ "$t" != "" ]]; then
        echo "notarization done!"
        # 制作升级文件
        break
    fi
    if [[ "$f" != "" ]]; then
        echo "$r"
        exit 1
    fi
    echo "公证还未完成，等待1分钟..."
    sleep 60
done

# 制作升级文件  这里是用的是 Sparkle 第三方库做升级
# 压缩 xxx.app  因为代码中解析压缩文件比dmg要快很多
/usr/bin/ditto -c -k --keepParent "$exportPath/浣熊市/浣熊市.app" "$zipPath"
./Pods/Sparkle/bin/sign_update $zipPath &> tmp  

r=`cat tmp`
edSignature=`echo ${r% *}`
length=`echo ${r#* }`

## 这里以后可以增加一个自动上传包到 oss

sed -i "" "s|sparkle:shortVersionString=.*|sparkle:shortVersionString=\"${currentVersionName}\"|" mac_update.xml
sed -i "" "s|sparkle:version.*|sparkle:version=\"${currentVersionCode}\"|" mac_update.xml
sed -i "" "s|length.*|${length}|" mac_update.xml
sed -i "" "s|sparkle:edSignature.*|${edSignature}|" mac_update.xml

```

# ExportOptions.plist 配置

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>compileBitcode</key>
	<false/>
	<key>destination</key>
	<string>export</string>
	<key>method</key>
	<string>developer-id（使用 developerid 导致）</string>
	<key>signingStyle</key>
	<string>manual （签名方式）</string>
    <key>signingCertificate</key>
    <string>Developer ID Application （签名证书）</string>
    <key>provisioningProfiles</key>  （描述文件）
        <dict>
            <key>com.xxxxx</key>
		    <string>DeveloperID  （自定义的描述文件名）</string>
        </dict>
	<key>stripSwiftSymbols</key>
	<true/>
	<key>teamID</key>
	<string>xxxxx</string>
	<key>thinning</key>
	<string>&lt;none&gt;</string>
</dict>
</plist>

```