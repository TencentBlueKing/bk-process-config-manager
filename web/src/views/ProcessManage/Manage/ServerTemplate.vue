<template>
    <div class="server-template">
        <ul>
            <li
                v-for="item in templateList"
                :key="item.id"
                @click="onTemplateClick(item)">
                <div :class="['template-list-item', { 'active': item.active }]" v-show="item.visible">
                    <i class="item-icon">{{ $t('模') }}</i>
                    <span v-bk-overflow-tips>{{item.name}}</span>
                </div>
            </li>
        </ul>
        <!-- <div class="not-server-template" v-if="!templateList.length">{{ $t('暂无服务模板数据') }}</div> -->
    </div>
</template>

<script>
    export default {
        props: {
            templateList: {
                type: Array,
                default: () => {
                    return []
                }
            }
        },
        methods: {
            onTemplateClick (val) {
                this.templateList.forEach(item => {
                    item.active = item.id === val.id
                })
                this.$emit('templateInfo', val)
            }
        }
    }
</script>

<style lang="postcss" scoped>
    .server-template {
        width: 100%;
        .template-list-item {
            height: 36px;
            width: 100%;
            color: #63656e;
            font-size: 14px;
            display: flex;
            align-items: center;
            cursor: pointer;
            padding: 0 16px;
            span {
                word-break:keep-all;
                white-space:nowrap;
                overflow:hidden;
                text-overflow:ellipsis;
            }
            .item-icon {
                height: 20px;
                width: 20px;
                border-radius: 50%;
                text-align: center;
                line-height: 20px;
                font-style: normal;
                font-size: 12px;
                background: #97aed6;
                color: #fff;
                flex-shrink: 0;
                margin-right: 7px;
            }
            &:hover {
                background-color: #e1ecff;
                transition: background-color .2s;
            }
        }
        .active {
            color: #3a84ff;
            background: #e1ecff;
            .item-icon {
                background: #3a84ff;
            }
        }
        .not-server-template {
            height: 100%;
            width: 100%;
            color: #63656e;
            display: flex;
            align-items: center;
            justify-content: center;
        }
    }
</style>
