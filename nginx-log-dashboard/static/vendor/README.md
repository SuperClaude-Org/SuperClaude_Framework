# static/vendor/ — 离线前端资源

本目录存放从 CDN 下载的 JS 文件，供无互联网环境使用。

在 **外网** 下载：

    curl -o static/vendor/vue.global.prod.js https://unpkg.com/vue@3/dist/vue.global.prod.js
    curl -o static/vendor/echarts.min.js https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js

或在外网运行 `python3 bundle_offline.py ./output` 一键生成完整离线包。

如果部署脚本 deploy_offline.py 检测到这两个文件，会自动切换 index.html 引用到本地路径。
