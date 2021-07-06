module.exports = {
    // commit message 格式
    // type(scope?): subject
    // example:
    // docs(input,radio): 输入框和单选框文档更新
    // feat(front): 在 scope 里面写上 front 方便筛选前端提交
    // Common types: [build,ci,chore,docs,feat,fix,perf,refactor,revert,style,test]
    extends: ['@commitlint/config-conventional'],
    // Available rules: https://commitlint.js.org/#/reference-rules
    // Level [0, 1, 2]: 0 disables the rule. For 1 it will be considered a warning for 2 an error.
    // Applicable [always,never]: never inverts the rule.
    // Value: value to use for this rule.
    rules: {
        'scope-empty': [2, 'never'],
        'type-enum': [
            2,
            'always',
            [
                'style', // '样式更新'
                'feat', // '新增功能'
                'fix', // '缺陷修复'
                'perf', // '性能优化'
                'optimize', // '功能优化'
                'refactor', // '重构代码(既没有新增功能，也没有修复 bug)'
                'test', // '新增测试用例或是更新现有测试'
                'docs', // '文档示例(documentation)'
                'build', // '项目构建、持续集成、工程化方面的提交'
                'revert',
                'chore' // '不属于以上类型的其他类型'
            ]
        ]
    }
}
