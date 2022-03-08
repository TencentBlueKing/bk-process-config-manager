# Release

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