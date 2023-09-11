# Release

## 1.0.25 - 2023-09-11 

### 🐛 Bugfixes

- bugfix:  适配进程操作重试报错 (closed #285)

- bugfix:  修改进程优先级报错 (closed #289)



**Full Changelog**: https://github.com/TencentBlueKing/bk-process-config-manager/compare/v1.0.24...v1.0.25


## 1.0.24 - 2023-07-21 

### 🚀 Features

- feature: IPv6 支持 (closed #263)

- feature:  更新 blueapps 框架 (closed #282)


### 🐛 Bugfixes

- bugfix:  同步CMDB配置异常 (closed #278)

- bugfix:  同步CMDB配置异常ProcessInst表适配 (closed #280)



**Full Changelog**: https://github.com/TencentBlueKing/bk-process-config-manager/compare/v1.0.23...v1.0.24


## 1.0.23 - 2023-04-21 

### 🚀 Features

- feat(front): 蓝鲸交互规范落地 - 文本溢出 & 空状态(closed #250)


### 🐛 Bugfixes

- bugfix: 修复指定多配置模板检查时部分检查结果未展示的问题 (fixed #254)

- fix(front): 进城管理 - 配置下发第二步表格宽度不正确(closed #257)

- bugfix: 修复配置文件名渲染功能失效的问题 (fixed #256)



**Full Changelog**: https://github.com/TencentBlueKing/bk-process-config-manager/compare/v1.0.22...v1.0.23


## 1.0.22 - 2022-10-28 

### 🐛 Bugfixes

- bugfix: 修复配置对比功能失效的问题 (#200)

- fix(front): 配置检查预览页查看无版本的配置实例出现系统异常 (closed #238)

- fix(front): 配置检查表达式过滤范围没有准确带入任务启动参数(closed #243)



**Full Changelog**: https://github.com/TencentBlueKing/bk-process-config-manager/compare/v1.0.21...v1.0.22


## 1.0.21 - 2022-10-14 

### 🚀 Features

- feature: API 在线文档在生产环境隐藏 (close #229)

- feature: 提供现网配置对比能力，修复多配置文件无法下发的问题 (#228 fixed #231)

- feat(front): 现网配置对比 (closed #228)


### 🐛 Bugfixes

- fix(front): safari浏览器中任务时间显示异常 (fixed #174)



**Full Changelog**: https://github.com/TencentBlueKing/bk-process-config-manager/compare/v1.0.20...v1.0.21


## 1.0.20 - 2022-09-13 

### 🚀 Features

- feature: 应用名称话术统一 (closed #202 closed #204)

- feat(front): 页面补充帮助文档链接 (closed #205)

- feature: 权限中心新增「业务运维」推荐权限 (#216)


### ✨ Optimizations

- optimization: 权限中心系统名称调整 (closed #201)

- optimize(front): 页面应用名称展示优化 (closed #203)


### 🐛 Bugfixes

- bugfix: 修复PaaSV2 admin 页面访问异常的问题 (fixed #211)

- bugfix: 修复仅具备业务访问权限可以操作任务重试的问题 (fixed #209)

- bugfix: 修复配置文件下发中搜索不存在的集群、模块等前端提示系统出现异常的问题 (fixed #208)

- fix(front): 按服务模板中当前业务暂无服务模版无法跳转配置平台 (closed #207)

- fix(front): 进程属性中搜索进程异常 (fixed #206)



**Full Changelog**: https://github.com/TencentBlueKing/bk-process-config-manager/compare/v1.0.19...v1.0.20


## 1.0.19 - 2022-09-01 

### 🚀 Features

- feature: 构建依赖升级 & title 补充 (closed #197)



**Full Changelog**: https://github.com/TencentBlueKing/bk-process-config-manager/compare/v1.0.18...v1.0.19


## 1.0.18 - 2022-08-25 

### 🚀 Features

- feature: 提供业务接入情况概览接口 (closed #193)


### ✏️ Docs

- docs: 开源信息更新 (closed #191)



**Full Changelog**: https://github.com/TencentBlueKing/bk-process-config-manager/compare/v1.0.17...v1.0.18


## 1.0.17 - 2022-06-23 

### 🚀 Features

- feat(front): 模板预览时报错样式优化 (closed #150)

- feature: process_status期望增加返回字段列表参数，支持只返回对应的字段列表 (close #146)


### 🐛 Bugfixes

- fix(front): 任务详情切换 Tab 后没有重置页数 (closed #170)

- bugfix: 修复部分服务模板较多的业务「进程属性」页面提示 CMDB 限频的问题 (fixed #165)



**Full Changelog**: https://github.com/TencentBlueKing/bk-process-config-manager/compare/v1.0.16...v1.0.17


## 1.0.16 - 2022-05-25 

### 🐛 Bugfixes

- bugfix: 修复进程优先级缺失情况下任务创建失败的问题 (closed #179)

- bugfix: 修复Windows 配置文件备份报错：The syntax of the command is incorrect. (closed #177)



**Full Changelog**: https://github.com/TencentBlueKing/bk-process-config-manager/compare/v1.0.15...v1.0.16


## 1.0.15 - 2022-05-12 

### 🚀 Features

- feature: 配置模板支持 replace 方法 (closed #154)

- feature: 进程操作支持按拓扑层级隔离 (closed #151)


### 🐛 Bugfixes

- fix(front): 打开不同业务的任务记录报错问题

- bugfix: 任务历史页面报错：系统错误 (fixed #158)

- bugfix: 部分进程优先级提前错误的情况下重试任务报错 (fixed #157)

- fix(front): 切换路由报错问题

- bugfix: 修复任务失败误判且多次通知的问题 (closed #168)



**Full Changelog**: https://github.com/TencentBlueKing/bk-process-config-manager/compare/v1.0.14...v1.0.15


## 1.0.14 - 2022-04-02 

### ✨ Optimizations

- optimization: 可观测性建设与鲁棒性提升(close #143)



**Full Changelog**: https://github.com/TencentBlueKing/bk-process-config-manager/compare/v1.0.13...v1.0.14


## 1.0.13 - 2022-03-14 

### 🐛 Bugfixes

- bugfix: 解决因DB问题导致的接口偶现超时等问题(fixed #140)



**Full Changelog**: https://github.com/TencentBlueKing/bk-process-config-manager/compare/v1.0.12...v1.0.13


## 1.0.12 - 2022-03-08 

### 🚀 Features

- feature: PaaS 镜像部署适配 (closed #135)

- feature: 修复转移主机到其他模块并修改该模块下进程启动数量导致同步CMDB进程配置失败的问题 (fixed #133)


### ✨ Optimizations

- optimization: mako渲染支持replace方法



**Full Changelog**: https://github.com/TencentBlueKing/bk-process-config-manager/compare/v1.0.11...v1.0.12


## 1.0.11 - 2022-01-20 

### 🐛 Bugfixes

- fix(front): 配置模板文件内容中换行符不对应问题 (closed #122)

- bugfix: 修复子任务状态更新失败的问题(fixed #130)



**Full Changelog**: https://github.com/TencentBlueKing/bk-process-config-manager/compare/v1.0.10...v1.0.11


## 1.0.10 - 2022-01-12 

### 🐛 Bugfixes

- bugfix: 修复windows换行符导致 (reopen #121)



**Full Changelog**: https://github.com/TencentBlueKing/bk-process-config-manager/compare/v1.0.9...v1.0.10


## 1.0.9 - 2022-01-11 

### 🚀 Features

- feature: PaaS容器部署适配 (closed #19)


### ✨ Optimizations

- style(front): 置文件下发详情页面中展示详细的输出格式信息 (close #110)


### 🐛 Bugfixes

- fix(front): 进程属性无服务模板时跳转 【配置平台】 无响应问题 (close #115)

- fix(front): 配置模板文件内容中换行符不对应问题 (closed #122)

- bugfix: 修复单个进程实例下发配置时一直提示需要生成新版本的问题 (fixed #121)



**Full Changelog**: https://github.com/TencentBlueKing/bk-process-config-manager/compare/v1.0.8...v1.0.9


## 1.0.8 - 2021-11-29 

### 🐛 Bugfixes

- bugfix: 修复迁移配置模板报错的问题 (fixed #112)



**Full Changelog**: https://github.com/TencentBlueKing/bk-process-config-manager/compare/v1.0.7...v1.0.8


## 1.0.7 - 2021-11-23 

### ✨ Optimizations

- optimization: 备份配置文件时保留时间属性(close #108)

- style(front): 任务历史失败后解决方案引导文本对齐（closed #99)

- optimization: GitHub Actions 自动发布流程优化 (closed #96)


### 🐛 Bugfixes

- bugfix: 修复任务历史失败解决方案引导有误的问题 (fixed #98)

- fix(front): 服务模板的表格分页点击失效 (close #105)

- bugfix: 修复任务历史失败指引跳转404问题 (fixed #102)



**Full Changelog**: https://github.com/TencentBlueKing/bk-process-config-manager/compare/v1.0.6...v1.0.7


## 1.0.6

- bugfix
  - 注销功能404 (closed #78)
- optimization
  - CMDB batch_create_proc_template 限制创建数量不大于100 (closed #89)

## 1.0.6

- optimization
  - CMDB batch_create_proc_template 限制创建数量不大于100 (closed #89)
- bugfix
  - 注销功能404 (closed #78)


## 1.0.5

- bugfix
  - 引导页进程管理路由跳转404 (closed #84)
  - 操作进程时主机的过滤条件没有生效(fixed #30)

## 1.0.4

- bugfix
  - 调用GSE接口未就绪时报错问题 (fixed #74)

## 1.0.3

- bugfix
  - 第三方系统请求API时报JWG校验错误问题 (fixed #66)
  - 备份文件后未下发配置 (fixed #71)
- feature
  - 增加测试点 (close

## 1.0.2

- bugfix
  - 修复进程启动数量修改导致配置下发报错的问题 (fixed #52)
- feature
  - 配置文件 - 路径提示文案优化 (fixed #50)
  - 配置预览 - 选择进程实例时，提示进程与配置文件的关联状态 (fixed #41)
  - 新添加了配置下发前自动备份往期配置文件的功能 (fixed #55)

## 1.0.1

- bugfix
  - 修复CMDB进程别名修改导致进程实例重复 (fixed #42)

## 1.0.0
- feature
    - 开放基础功能