<template>
    <div class="process-info">
        <!-- 配置文件 -->
        <div class="config-file">
            <div class="instance-title">
                <span class="instance-title-text">{{ isServiceInstance ? $t('配置文件') : $t('服务模版配置文件') }}</span>
                <div class="instance-title-content" @click="onConfigFile">
                    <i class="title-icon gsekit-icon gsekit-icon-edit-fill"></i>
                    <span>{{ $t('配置') }}</span>
                </div>
            </div>
            <div class="config-file-table">
                <bk-table v-if="tableData.length"
                    auto-scroll-to-top
                    header-row-class-name="header"
                    :data="tableData"
                    :outer-border="false"
                    :header-border="false"
                    :header-cell-style="{ background: '#fff' }">
                    <bk-table-column label="ID" prop="config_template_id"></bk-table-column>
                    <bk-table-column :label="$t('模板名称')" prop="file_name"></bk-table-column>
                    <bk-table-column :label="$t('文件名称')" prop="template_name"></bk-table-column>
                </bk-table>
                <bk-exception v-else class="exception-wrap-item exception-part" type="empty" scene="part">
                    <span class="no-config-file">{{ $t('没有配置文件') }}</span>
                    <bk-button :theme="'primary'" @click="onConfigFile">{{ $t('配置') }}</bk-button>
                </bk-exception>
            </div>
        </div>
        <!-- 进程属性 -->
        <div class="process-attr">
            <div class="instance-title">
                <span class="instance-title-text">{{ isServiceInstance ? $t('进程属性') : $t('服务模版进程属性') }}</span>
                <div class="instance-title-content" @click="onEditor">
                    <i class="title-icon gsekit-icon gsekit-icon-edit-fill"></i>
                    <span>{{ $t('编辑') }}</span>
                    <span v-if="!currentProcess.is_full" class="warn-prompt">
                        <i class="gsekit-icon gsekit-icon-incomplete-line"></i>
                        <span>{{ $t('进程管理的必填信息不完整') }}</span>
                    </span>
                </div>
            </div>
            <div class="process-attr-content">
                <span class="attr-title">{{ $t('基础信息') }}</span>
                <div class="attr-content">
                    <div class="content-item" v-for="item in baseInfo" :key="item.id">
                        <label class="content-item-label">{{ item.name }}</label>
                        <span class="content-item-span" v-bk-overflow-tips>
                            {{ processInfo[item.key] || '--' }}
                        </span>
                    </div>
                </div>
            </div>
            <div class="process-attr-content">
                <span class="attr-title">{{ $t('进程管理信息') }}</span>
                <div class="attr-content">
                    <div class="content-item" v-for="item in processAttrInfo" :key="item.id">
                        <span v-if="item.isrequired" class="warn-icon" v-bk-tooltips="$t('必填项')">*</span>
                        <label class="content-item-label">{{ item.name }}</label>
                        <span class="content-item-span" v-if="processInfo[item.key]" v-bk-overflow-tips>
                            {{ processInfo[item.key] }}
                        </span>
                        <span class="content-item-span" v-else>
                            <span v-if="item.isrequired" class="quire-empty" v-bk-tooltips="$t('进程管理必填项未填写')">{{ '--' }}</span>
                            <span v-else>{{ '--' }}</span>
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        props: {
            tableData: {
                type: Array,
                default: () => {
                    return []
                }
            },
            currentProcess: {
                type: Object,
                default: () => {
                    return {}
                }
            },
            baseInfo: {
                type: Array,
                default: () => {
                    return []
                }
            },
            processAttrInfo: {
                type: Array,
                default: () => {
                    return []
                }
            },
            processInfo: {
                type: Object,
                default: () => {
                    return {}
                }
            },
            isServiceInstance: {
                type: Boolean,
                default: true
            }
        },
        methods: {
            onConfigFile () {
                this.$emit('onConfigFile')
            },
            onEditor () {
                this.$emit('onEditor')
            }
        }
    }
</script>

<style lang="postcss" scoped>
    .config-file {
        position: relative;
        width: 100%;
        background-color: #fff;
        box-shadow: 0px 1px 2px 0px rgba(0,0,0,0.1);
        padding: 16px 20px;
        margin-bottom: 16px;
        /deep/ .header {
            .cell {
                background: #f5f6fa;
            }
        }
        /deep/ .exception-wrap-item {
            margin-bottom: 10px;
            font-size: 14px;
            color: #63656e;
            .no-config-file {
                display: block;
                margin-bottom: 10px;
            }
        }
    }
    .process-attr {
        position: relative;
        width: 100%;
        background-color: #fff;
        box-shadow: 0px 1px 2px 0px rgba(0,0,0,0.1);
        padding: 16px 20px;
        font-size: 14px;
        .attr-title {
            color: #63656e;
            font-weight: 700;
        }
        .attr-content {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            color: #979ba5;
            padding: 16px 0;
            .content-item {
                padding: 0 25px;
                width: 338px;
                height: 44px;
                position: relative;
                display: flex;
                align-items: center;
                cursor: default;
                .warn-icon {
                    color: #ea3636;
                    font-style: normal;
                    position: absolute;
                    top: 15px;
                    left: 10px;
                    font-weight: 700;
                }
                .content-item-label {
                    min-width: 90px;
                    display: inline-block;
                    text-align: left;
                    position: relative;
                    margin-right: 10px;
                    &::after {
                        content: ':';
                        position: absolute;
                        right: -5px;
                        top: 0;
                        font-weight: 700;
                        color: #63656e;
                    }
                }
                .content-item-span {
                    flex: 1;
                    color: #63656e;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                    display: inline-block;
                    .quire-empty {
                        color: #ff9c01;
                    }
                }
            }
        }
    }
    @media screen and (min-width: 960px) and (max-width: 1380px) {
        .attr-content {
            .content-item {
                width: 50% !important;
            }
        }
    }
    @media screen and (min-width: 1380px) and (max-width: 1680px) {
        .attr-content {
            .content-item {
                width: 33.33% !important;
            }
        }
    }
    @media screen and (min-width: 1680px) {
        .attr-content {
            .content-item {
                width: 33.33% !important;
            }
        }
    }
    .instance-title {
        display: flex;
        align-items: center;
        color: #3a84ff;
        font-size: 14px;
        margin-bottom: 19px;
        .instance-title-text {
            font-size: 16px;
            color: #313238;
            margin-right: 18px;
            &::before {
                content: '';
                position: absolute;
                left: 0;
                top: 20px;
                width: 4px;
                height: 15px;
                background: #dcdee5;
            }
        }
        .instance-title-content {
            display: flex;
            align-items: center;
            cursor: pointer;
            .title-icon  {
                margin-right: 8px;
                font-size: 16px;
            }
            .warn-prompt {
                margin-left: 12px;
                color: #ff9c01;
                span {
                    margin-left: 7px;
                }
            }
        }
    }
</style>
