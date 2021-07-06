<template>
    <div class="editor-attribute" v-bkloading="{ isLoading }">
        <div class="special-tip" v-if="!isAddProcess && !isServiceInstance">
            <i class="special-tip-icon bk-icon icon-info"></i>
            <div>{{ $t('编辑将会对所有使用') + templateName + $t('服务模版的') + currentProcess.bk_process_name + $t('进程生效，编辑后需到') }}
                <span class="config-platform" @click="goConfigPlatform">{{ $t('配置平台') }}</span>{{$t('同步。')}}</div>
        </div>
        <bk-form :model="formData" :rules="rules" ref="attribute">
            <div class="editor-attribute-content">
                <span class="attribute-content-title">{{ $t('基础信息') }}</span>
                <div class="attribute-content-wrapper">
                    <div class="wrapper-item" v-for="item in baseInfo" :key="item.key">
                        <bk-form-item
                            :property="item.key">
                            <label class="wrapper-item-label">
                                <bk-popover v-if="objAttribute[item.key] && objAttribute[item.key].placeholder">
                                    <span class="dashed-underline">{{ item.name }}</span>
                                    <span slot="content" v-html="objAttribute[item.key].placeholder"></span>
                                </bk-popover>
                                <span v-else>{{ item.name }}</span>
                                <i v-if="item.isrequired" class="warn-icon">*</i>
                                <bk-popover v-if="objAttribute[item.key] && objAttribute[item.key].isreadonly">
                                    <span class="popover-icon gsekit-icon gsekit-icon-cc-lock"></span>
                                    <span slot="content" v-html="objAttribute[item.key].isreadonly"></span>
                                </bk-popover>
                            </label>
                            <template v-if="item.isrequired">
                                <bk-input :disabled="!isAddProcess && isServiceInstance" v-model="formData[item.key]" clearable :maxlength="256" :placeholder="item.placeholder"></bk-input>
                            </template>
                            <bk-input
                                v-else-if="item.key === 'bk_start_param_regex'"
                                :placeholder="item.placeholder"
                                v-model="formData[item.key]"
                                :type="'textarea'"
                                :rows="3"></bk-input>
                            <template v-else>
                                <bk-input v-if="formData[item.key]" v-model="formData[item.key]" clearable :maxlength="256" :placeholder="item.placeholder"></bk-input>
                                <bk-input v-else v-model="formData[item.key]" :placeholder="item.placeholder"></bk-input>
                            </template>
                        </bk-form-item>
                    </div>
                </div>
            </div>
            <div class="editor-attribute-content">
                <span class="attribute-content-title">{{ $t('进程管理信息') }}</span>
                <div class="attribute-content-wrapper">
                    <div class="wrapper-item" v-for="item in processAttrInfo" :key="item.key">
                        <bk-form-item
                            :property="item.key">
                            <label class="wrapper-item-label">
                                <bk-popover v-if="objAttribute[item.key] && objAttribute[item.key].placeholder">
                                    <span class="dashed-underline">{{ item.name }}</span>
                                    <span slot="content" v-html="objAttribute[item.key].placeholder"></span>
                                </bk-popover>
                                <span v-else>{{ item.name }}</span>
                                <i v-if="item.isrequired" class="warn-icon">*</i>
                            </label>
                            <template v-if="item.hasAppend">
                                <bk-input v-model="formData[item.key]" type="number" :show-controls="false" :placeholder="item.placeholder">
                                    <template slot="append">
                                        <div class="group-text">s</div>
                                    </template>
                                </bk-input>
                            </template>
                            <template v-else-if="item.isNumber">
                                <bk-input type="number" :show-controls="false" v-model="formData[item.key]" :placeholder="item.placeholder"></bk-input>
                            </template>
                            <bk-input v-else v-model="formData[item.key]" clearable :placeholder="item.placeholder"></bk-input>
                        </bk-form-item>
                    </div>
                </div>
            </div>
        </bk-form>
        <div class="config-options">
            <bk-button @click="onSaveEditor" :loading="isSaveConfigIng" :theme="'primary'">{{ $t('保存') }}</bk-button>
            <bk-button @click="onCancel">{{ $t('取消') }}</bk-button>
        </div>
    </div>
</template>

<script>
    import rules from './attributeEditRule'
    export default {
        props: {
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
            },
            templateName: {
                type: String,
                default: ''
            },
            currentProcess: {
                type: Object,
                default: () => {
                    return {}
                }
            },
            mandatory: {
                type: Array,
                default: () => {
                    return []
                }
            },
            isAddProcess: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
                isSaveConfigIng: false,
                activeName: ['processAttrInfo'],
                formData: {},
                rules,
                objAttribute: {},
                isLoading: false
            }
        },
        watch: {
            processInfo: {
                handler (val) {
                    const processInfo = JSON.parse(JSON.stringify(val))
                    const formData = {}
                    for (const key of Object.keys(processInfo)) {
                        // 传auto_start会报错
                        if (key !== 'auto_start') {
                            formData[key] = key === 'bind_info' ? [] : ''
                        }
                    }
                    this.formData = this.isAddProcess ? formData : processInfo
                    this.formData.proc_num = this.formData.proc_num || 1
                },
                immediate: true,
                deep: true
            }
        },
        created () {
            this.getObjAttribute()
        },
        methods: {
            onSaveEditor () {
                this.$refs.attribute.validate().then(async validator => {
                    this.isSaveConfigIng = true
                    for (const key in this.formData) {
                        const numType = ['timeout', 'bk_start_check_secs', 'proc_num', 'priority']
                        if (numType.includes(key)) {
                            if (this.formData[key]) {
                                this.formData[key] = Number(this.formData[key])
                            } else {
                                this.formData[key] = null
                            }
                        }
                    }
                    if (this.isAddProcess) { // 新增进程
                        this.onAddProcess()
                    } else { // 修改进程
                        this.onEditorProcess()
                    }
                }).catch(error => {
                    console.warn(error)
                })
            },
            // 新增进程
            async onAddProcess () {
                try {
                    const { serviceId } = this.$route.params
                    if (this.isServiceInstance) {
                        const res = await this.$store.dispatch('process/ajaxCreateProcessInstance', {
                            data: {
                                service_instance_id: Number(serviceId),
                                process_property: this.formData
                            }
                        })
                        if (res.result) {
                            this.$bkMessage({
                                message: this.$t('进程新增成功'),
                                theme: 'success'
                            })
                        }
                    } else {
                        const res = await this.$store.dispatch('process/ajaxCreateProcessTemplate', {
                            data: {
                                service_template_id: Number(serviceId),
                                process_property: this.formData
                            }
                        })
                        if (res.result) {
                            const h = this.$createElement
                            this.$bkMessage({
                                message: h('p', {
                                    style: {
                                        margin: 0
                                    }
                                }, [
                                    this.$t('进程新增成功，请到'),
                                    h('span', {
                                        style: {
                                            color: '#3A84FF',
                                            cursor: 'pointer'
                                        },
                                        on: {
                                            click: () => {
                                                const cmdbUrl = window.PROJECT_CONFIG.CMDB_URL
                                                const bizId = this.$store.state.bizId
                                                window.open(cmdbUrl + `/#/business/${bizId}/service/operational/template/${this.currentProcess.service_template_id}?tab=instance`)
                                            }
                                        }
                                    }, this.$t('配置平台')),
                                    this.$t('进行同步')
                                ]),
                                theme: 'success',
                                ellipsisLine: 2
                            })
                        }
                    }
                    this.$emit('onCreateProcess')
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.isSaveConfigIng = false
                }
            },
            // 修改进程
            async onEditorProcess () {
                try {
                    if (this.isServiceInstance) {
                        const res = await this.$store.dispatch('process/ajaxUpdateProcessInstance', {
                            data: {
                                process_property: this.formData
                            }
                        })
                        if (res.result) {
                            this.$bkMessage({
                                message: this.$t('进程属性编辑成功'),
                                theme: 'success'
                            })
                        }
                    } else {
                        const res = await this.$store.dispatch('process/ajaxUpdateProcessTemplate', {
                            data: {
                                process_template_id: this.currentProcess.id,
                                process_property: this.formData
                            }
                        })
                        if (res.result) {
                            const h = this.$createElement
                            this.$bkMessage({
                                message: h('p', {
                                    style: {
                                        margin: 0
                                    }
                                }, [
                                    this.$t('模版进程属性编辑成功，需要到'),
                                    h('span', {
                                        style: {
                                            color: '#3A84FF',
                                            cursor: 'pointer'
                                        },
                                        on: {
                                            click: () => {
                                                const cmdbUrl = window.PROJECT_CONFIG.CMDB_URL
                                                const bizId = this.$store.state.bizId
                                                window.open(cmdbUrl + `/#/business/${bizId}/service/operational/template/${this.currentProcess.service_template_id}?tab=instance`)
                                            }
                                        }
                                    }, this.$t('配置平台')),
                                    this.$t('同步,方可对其他使用模板的进程生效')
                                ]),
                                theme: 'success',
                                ellipsisLine: 2
                            })
                        }
                    }
                    this.$emit('onSaveEditor')
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.isSaveConfigIng = false
                }
            },
            onCancel () {
                this.$emit('onCancel')
            },
            goConfigPlatform () {
                window.open(window.PROJECT_CONFIG.CMDB_URL
                    + `/#/business/${this.$store.state.bizId}/service/operational/template/${this.currentProcess.service_template_id}?tab=instance`)
            },
            // 获取对象模型属性
            async getObjAttribute () {
                try {
                    this.isLoading = true
                    const res = await this.$store.dispatch('cmdb/ajaxGetProcessInstanceList')
                    res.data.forEach(item => {
                        this.objAttribute[item.bk_property_id] = item
                    })
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.isLoading = false
                }
            }
        }
    }
</script>

<style lang='postcss' scoped>
    .editor-attribute {
        width: 100%;
        padding: 26px 60px 20px 30px;
        .special-tip {
            width: 100%;
            height: 32px;
            display: flex;
            align-items: center;
            background: #f0f8ff;
            border: 1px solid #c5daff;
            border-radius: 2px;
            color: #63656e;
            font-size: 12px;
            margin-bottom: 15px;
            .special-tip-icon {
                font-size: 14px;
                color: #3a84ff;
                margin: 1px 3px 0 11px;
            }
            .config-platform {
                color: #009dff;
                margin-right: 3px;
                cursor: pointer;
            }
        }
        .attribute-content-title {
            font-size: 14px;
            color: #63656e;
            font-weight: 700;
        }
        .attribute-content-wrapper {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            font-size: 14px;
            padding: 16px 0 16px 20px;
            color: #63656e;
            .wrapper-item {
                width: 320px;
                line-height: 32px;
                position: relative;
                &.listen-info {
                    margin-bottom: 10px;
                }
                .bk-form-item {
                    width: 100%;
                    margin-bottom: 15px;
                    /deep/ .bk-form-content {
                        margin: 0 !important;
                        .bk-icon {
                            top: 40px;
                        }
                    }
                    .wrapper-item-label {
                        margin-bottom: 5px;
                    }
                }
                .wrapper-item-label {
                    min-width: 90px;
                    display: block;
                    text-align: left;
                    position: relative;
                    margin-right: 10px;
                    .popover-icon {
                        color: #c3cdd7;
                        font-size: 16px;
                        line-height: 16px;
                    }
                    .dashed-underline {
                        line-height: 25px;
                        display: inline-block;
                        position: relative;
                        border-bottom: 1px dashed #c4c6cc;
                    }
                }
                .group-text {
                    background: #fafbfd;
                    width: 31px;
                    padding: 0;
                    text-align: center;
                }
                .warn-icon {
                    color: #EA3636;
                    font-style: normal;
                    font-weight: 700;
                }
                .wrapper-item-span {
                    color: #63656e;
                }
                /deep/ .bk-form-textarea {
                    min-height: 57px;
                }
            }
        }
        
        /deep/ .bk-form .bk-form-content {
            line-height: 28px
        }
        .config-options {
            margin-left: 20px;
            .bk-button {
                width: 86px;
                margin-right: 5px;
            }
        }
    }
</style>
