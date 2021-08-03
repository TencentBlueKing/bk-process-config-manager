module.exports = {
    defaultSeverity: 'error',
    extends: ['@bkui/stylelint-config-bk'],
    rules: {
        // 不能用 important
        'declaration-no-important': null,
    }
}