- 基本语法  

    https://www.runoob.com/linux/linux-shell-passing-arguments.html
    
    - 字符串操作 

        https://www.cnblogs.com/fengbohello/p/5954895.html
        https://blog.csdn.net/Mr_LeeHY/article/details/76383091

- 从命令中读取参数 
    
    https://blog.51cto.com/steed/2443313




例子： 一个 flutter 构建 apk 的自动打包脚本

```s
#!/bin/bash
# android 自动打包脚本，支持设置 versionName， versionCode， 编译环境，服务器环境， 打包完成 versionName 自动+1，版本记录在 version.txt 中
# -vc versionCode
# -vn versionName
# -st 服务器接口环境 默认为 debug
# -bt 编译环境      默认为 --release
# -clean 打包前clean一下工程

currentVersionName="1.0.1.1001"
currentVersionCode=75

# 读取当前版本号
while read line
    do
        k=${line%=*}
        v=${line#*=}
        if [ ${k} = "android_version_name" ]; then
            currentVersionName=${line#*=}
        elif [ ${k} = "android_version_code" ]; then
            currentVersionCode=${line#*=}
        fi
done < version.txt

echo "currentVersionName:   ${currentVersionName}"
echo "currentVersionCode:   ${currentVersionCode}"

# 生成新的版本号
newVersionCode=${currentVersionCode}
newVersionName=${currentVersionName}
smallNum=`expr ${currentVersionName:0-4} + 1`
startLength=`expr ${#newVersionName} - 4`
newVersionName=${newVersionName:0:startLength}${smallNum}

buildType="--release"
serviceType="debug"
clean="false"

# 解析命令中的参数
while [ -n "$1" ]
do
    case "$1" in
        -vc) newVersionCode="$2"
            shift ;;
        -vn) newVersionName="$2"
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

# flutter 打包
echo "flutter build apk --target-platform android-arm --flavor hhh ${buildType} -v  --dart-define=SERVER_TYPE=${serviceType} --build-name ${newVersionName}  --build-number ${newVersionCode}"

flutter build apk --target-platform android-arm --flavor hxs ${buildType} -v  --dart-define=SERVER_TYPE=${serviceType} --build-name ${newVersionName}  --build-number ${newVersionCode}

if [ $? -ne 0 ]; then
    echo "build failed"
    exit 1
else
    echo "build success"
fi

# 修改记录的版本号

sed -i "" "s/android_version_name=${currentVersionName}/android_version_name=${newVersionName}/" version.txt
sed -i "" "s/android_version_code=${currentVersionCode}/android_version_code=${newVersionCode}/" version.txt

# 修改文件名
path="./build/app/outputs/flutter-apk/"
if [ "${buildType}" = "--release" ];then
    mv "${path}app-hhh-release.apk" "${path}hxs_release_${newVersionName}.apk"
elif [ "${buildType}" = "--debug" ];then
    mv "${path}app-hhh-debug.apk" "${path}hxs_debug_${newVersionName}.apk"
fi

if [ $? -ne 0 ]; then
    echo "rename failed"
    exit 1
else
    echo "rename success"
fi

```