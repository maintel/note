# unable to load script from assets 'index.android bundle'  ,make sure your bundle is packaged correctly or youu're runing a packager server

引入到 Android studio 中和 源生 Android 结合起来是，运行报错

> unable to load script from assets 'index.android bundle'  ,make sure your bundle is packaged correctly or youu're runing a packager server

*解决办法*：

- 在 root/app/src/main 下新建 assets 文件夹；
- 在 Terminal 执行：

    react-native bundle --platform android --dev false --entry-file index.android.js --bundle-output app/src/main/assets/index.android.bundle --assets-dest app/src/main/res/

- 重新运行程序。

# undefined is not an object (evaluating 'nr.ReactCurrentOwner')

首先检查 react 版本是否大于 0.45，并且 react 版本是否大于 16.0.0-alpha.12，如果 react 版本不满足则在当前根目录下执行：

> npm i -S react@16.0.0-alpha.12

然后重新运行项目。

如果上面的情况满足，则检查是否执行了 `npm start`。

