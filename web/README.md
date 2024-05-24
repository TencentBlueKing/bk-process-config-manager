gsekit-web
===

## 使用

``` bash
# 本地运行蓝鲸前端开发脚手架的文档工程
npm run doc

# 构建蓝鲸前端开发脚手架的文档工程
npm run build:doc

# 本地开发
npm run dev

# 创建 `Dll bundle`
npm run dll

# 打包构建
npm run build

# 打包构建分析
npm run build:analyzer
```
// npm run doc 执行后无效，这里注释了

# 补充说明，环境搭建
1.dev.env.js中的LOCAL_DEV_URL:JSON.stringify('http://dev.xxx.com');// hosts配置 127.0.0.1 dev.xxx.com
2.index-dev.html中const AJAX_URL_PREFIX = 'http://xxx.com/';
1和2的xxx是一样的，2中的http://xxx.com要是能访问的线上环境（gsekit的测试环境，预发布环境等）
```
