<template>
    <bk-tag-input ref="tagInputRef"
        class="king-tag-input"
        allow-create
        placeholder="*"
        :list="localList"
        :value="localValue"
        :paste-fn="pasteFn"
        :clearable="false"
        @change="handleChange"
    ></bk-tag-input>
</template>

<script>
    export default {
        props: {
            list: {
                type: Array,
                required: true
            },
            value: {
                type: Array,
                required: true
            },
            name: {
                type: String,
                default: ''
            }
        },
        data () {
            return {
                localList: [],
                localValue: []
            }
        },
        watch: {
            list: {
                handler (val) {
                    this.localList = [
                        { id: 'SELECT_ALL', name: this.$t('全部') + this.name + '（*）' },
                        ...val
                    ]
                },
                immediate: true
            },
            value: {
                handler (val) {
                    if (!this.isSame(val, this.localValue)) {
                        this.localValue = val
                    }
                },
                immediate: true
            }
        },
        methods: {
            // 两个列表是否选中的同样的 id
            isSame (source, target) {
                const isArray = Array.isArray(source) && Array.isArray(target)
                if (isArray) {
                    if (source.length !== target.length) {
                        return false
                    }
                    return !source.some((value, index) => value !== target[index])
                }
                return source === target
            },
            // 选中成员改变
            handleChange (tagList) {
                const newValue = [...tagList]
                if (newValue.includes('SELECT_ALL')) { // 选择全部等于什么都不选
                    this.$nextTick(() => {
                        this.localValue = []
                        this.$emit('change', [])
                    })
                } else { // [1, 2]
                    this.localValue = newValue
                    this.$emit('change', newValue)
                }
            },
            // 标签输入框处理粘贴事件
            pasteFn (val) {
                const pasteValues = val.split(',').map(item => item.trim()).filter(Boolean)
                const result = [...new Set([...this.localValue, ...pasteValues])]
                this.handleChange(result)
            }
        }
    }
</script>

<style scoped>
    @import "../../css/variable.css";
    .king-tag-input {
        height: 30px !important;
        min-height: 30px !important;
        min-width: 48px;
        /deep/ .bk-tag-input {
            height: 30px !important;
            min-height: 30px !important;
            padding: 0 0 0 12px;
            border: none;
            .tag-list {
                .key-node {
                    height: 20px;
                    margin: 0;
                    border: none !important;
                    background-color: transparent;
                    .tag {
                        padding: 0;
                        background-color: transparent;
                        .text::after {
                            content: '，';
                            width: 12px;
                            height: 20px;
                            line-height: 20px;
                            transition: opacity .2s;
                        }
                    }
                    &:last-child .tag .text::after, &.remove-comma .tag .text::after {
                        opacity: 0;
                        transition: opacity .2s;
                    }
                }
                .staff-input {
                    height: 20px;
                    margin: 0;
                    border: none;
                    background-color: transparent;
                    .input {
                        height: 20px;
                        line-height: 20px;
                    }
                }
            }
            .placeholder {
                left: 20px;
            }
            &.active {
                .text {
                    color: $newMainColor;
                }
            }
        }
    }
</style>
