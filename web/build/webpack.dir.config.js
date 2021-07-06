// 供 WebStorm 解析文件引用
const path = require('path')

module.exports = {
    resolve: {
        alias: {
            '@': path.resolve(__dirname, '../src')
        }
    }
}
