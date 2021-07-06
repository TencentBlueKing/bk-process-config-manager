<template>
    <bk-select v-if="list.length > 50"
        :value="value"
        :placeholder="$t('全部') + name + '（*）'"
        :popover-min-width="160"
        :list="list"
        multiple
        searchable
        enable-virtual-scroll
        @change="handleChange">
    </bk-select>
    <bk-select v-else
        :value="value"
        :placeholder="$t('全部') + name + '（*）'"
        :popover-min-width="160"
        multiple
        searchable
        @change="handleChange">
        <template v-for="item in list">
            <bk-option :key="item.id" :id="item.id" :name="item.name"></bk-option>
        </template>
    </bk-select>
    <!--<bk-select :value="value"
        :placeholder="name"
        :clearable="false"
        :popover-min-width="160"
        multiple
        searchable
        @selected="handleChange">
        <bk-option id="*" :name="$t('全部') + name + '（*）'"></bk-option>
        <template v-for="item in list">
            <bk-option :key="item.id" :id="item.id" :name="item.name">
                <div class="bk-option-content-default king-option-container">
                    <i class="bk-option-icon bk-icon icon-check-1" v-if="value.includes(item.id)"></i>
                    <div v-bk-overflow-tips="{ placement: 'right', content: item.name }" class="bk-option-name">
                        {{ item.name }}
                    </div>
                </div>
            </bk-option>
        </template>
    </bk-select>-->
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
        methods: {
            handleChange (val) {
                this.$emit('change', val)
            }
            // handleChange (val) {
            //     if (val[val.length - 1] === '*') { // 选择了全部
            //         document.body.click() // 手动关闭多选下拉框
            //         this.$emit('change', ['*'])
            //     } else if (val[0] === '*') { // 之前是全部，单选了某个选项
            //         this.$emit('change', val.slice(1))
            //     } else {
            //         this.$emit('change', val)
            //     }
            // }
        }
    }
</script>

<!--<style scoped>-->
<!--    .king-option-container {-->
<!--        display: flex;-->
<!--        align-items: center;-->
<!--        width: 100%;-->
<!--        .bk-option-icon {-->
<!--            flex-shrink: 0;-->
<!--            &~.bk-option-name {-->
<!--                padding-right: 0;-->
<!--                margin-right: 20px;-->
<!--            }-->
<!--        }-->
<!--    }-->
<!--</style>-->
