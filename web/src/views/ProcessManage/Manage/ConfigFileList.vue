<template>
    <div class="config-file-list">
        <div class="input-search">
            <bk-input
                v-model.trim="searchWord"
                :placeholder="$t('请输入文件名或模板名')"
                :right-icon="'bk-icon icon-search'"
                clearable
                @blur="handleSearch"
                @enter="handleSearch"
                @clear="handleSearch"></bk-input>
        </div>
        <div class="config-file-prompt">
            <span class="color-burn">{{ $t('选择配置文件') }}</span>
            <span>{{ $t('(已选') }}</span>
            <span class="file-count">{{ selectFile.length }}</span>
            <span>{{ $t('个)') }}</span>
        </div>
        <bk-table
            ref="configFileTable"
            :max-height="$store.state.pageHeight - 266"
            :data="tableData"
            :pagination="pagination"
            v-bkloading="{ isLoading: isDataLoading }"
            @select="handleSelect"
            @select-all="handleSelectAll"
            @page-change="handlePageChange"
            @page-limit-change="handlePageLimitChange">
            <bk-table-column type="selection" width="60"></bk-table-column>
            <bk-table-column label="ID" width="100" prop="config_template_id" :sortable="true"></bk-table-column>
            <bk-table-column :label="$t('模板名称')" prop="template_name">
                <div slot-scope="props" v-bk-overflow-tips>
                    {{ props.row.template_name || '--' }}
                </div>
            </bk-table-column>
            <bk-table-column :label="$t('文件名称')" prop="file_name"></bk-table-column>
            <template slot="empty">
                <bk-exception class="exception-wrap-item exception-part" type="empty" scene="part">
                    <span>{{ $t('暂无配置文件') }}</span>
                    <div class="button-text" @click="routeConfigTemplateList">
                        {{ $t('新建文件') }}
                    </div>
                </bk-exception>
            </template>
        </bk-table>
        <div class="config-options">
            <bk-button @click="onBindConfigFile" :loading="isSaveComplete" :theme="'primary'">{{ $t('保存') }}</bk-button>
            <bk-button @click="onCancel">{{ $t('取消') }}</bk-button>
        </div>
    </div>
</template>

<script>
    export default {
        props: {
            isBindingData: {
                type: Array,
                default () {
                    return []
                }
            },
            currentProcess: {
                type: Object,
                default () {
                    return {}
                }
            },
            isServiceInstance: {
                type: Boolean,
                default: true
            }
        },
        data () {
            return {
                pagination: {
                    current: 1,
                    count: 210,
                    limit: 50
                },
                searchWord: '',
                searchedWord: '',
                selectFile: [],
                isDataLoading: false,
                tableData: [],
                isSaveComplete: false
            }
        },
        mounted () {
            this.getTemplateList()
        },
        methods: {
            // 获取配置文件列表
            async getTemplateList () {
                try {
                    this.isDataLoading = true
                    const bindingID = this.isBindingData.map(item => {
                        return item.config_template_id
                    })
                    const res = await this.$store.dispatch('configTemplate/ajaxGetNewConfigTemplateList', {
                        data: {
                            search: this.searchWord,
                            page: this.pagination.current,
                            pagesize: this.pagination.limit,
                            binding_config_template_ids: bindingID
                        }
                    })
                    this.tableData = res.data.list
                    this.pagination.count = res.data.count
                    this.$nextTick(() => {
                        this.selectFile = []
                        this.tableData.forEach(item => {
                            if (bindingID.length && bindingID.includes(item.config_template_id)) {
                                this.selectFile.push(item)
                                this.$refs.configFileTable.toggleRowSelection(item, true)
                            }
                        })
                    })
                    this.searchedWord = this.searchWord
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.isDataLoading = false
                }
            },
            // 切换页
            handlePageChange (page) {
                this.pagination.current = page
                this.getTemplateList()
            },
            handlePageLimitChange (limit) {
                this.pagination.current = 1
                this.pagination.limit = limit
                this.getTemplateList()
            },
            // 勾选checkbox
            handleSelect (selection) {
                this.selectFile = selection
            },
            // 全选
            handleSelectAll (selection) {
                this.selectFile = selection
            },
            // 确认绑定
            async onBindConfigFile () {
                try {
                    this.isSaveComplete = true
                    const currentProcess = this.currentProcess
                    const res = await this.$store.dispatch('configTemplate/ajaxBindProcessToTemplate', {
                        data: {
                            config_template_id_list: this.selectFile.map(item => item.config_template_id),
                            process_object_type: this.isServiceInstance ? 'INSTANCE' : 'TEMPLATE',
                            process_object_id: this.isServiceInstance ? currentProcess.property.bk_process_id : currentProcess.id
                        }
                    })
                    const { created_relations_count: createdCount, deleted_relations_count: deltedCount } = res.data
                    if (createdCount + deltedCount > 0) {
                        this.$bkMessage({
                            message: this.$t('成功关联') + createdCount + this.$t('个配置') + '，' + this.$t('删除') + deltedCount + this.$t('个配置'),
                            theme: 'success'
                        })
                    }
                    this.$emit('onBindConfigFile')
                } catch (error) {
                    console.warn(error)
                } finally {
                    this.isSaveComplete = false
                }
            },
            // 取消
            onCancel () {
                this.$emit('onCancel')
            },
            // 输入框搜索
            handleSearch () {
                if (this.searchedWord !== this.searchWord) {
                    this.getTemplateList()
                }
            },
            // 去配置文件页面
            routeConfigTemplateList () {
                const siteUrl = window.PROJECT_CONFIG.SITE_URL
                const bizId = this.$store.state.bizId
                window.open(`${window.origin}${siteUrl}/config-file?biz=${bizId}&fromPreManage=true`, '_self')
            }
        }
    }
</script>

<style lang="postcss" scoped>
    .config-file-list {
        padding: 30px 30px 0;
        .input-search {
            margin-bottom: 16px;
        }
        /deep/ .bk-table {
            max-height: 550px;
            margin-top: 0;
            .bk-table-empty-text {
                padding: 10px 0 60px;
                .button-text {
                    margin-top: 10px;
                    font-size: 12px;
                }
            }
        }
        .config-file-prompt {
            height: 42px;
            background: #f0f1f5;
            border: 1px solid #dcdee5;
            border-radius: 2px 0px 0px 2px;
            padding-left: 16px;
            color: #979ba5;
            font-size: 12px;
            line-height: 42px;
            margin-bottom: -1px;
            font-weight: 700;
            .color-burn {
                color: #63656e;
            }
            .file-count {
                color: #3a84ff;
            }
        }
        .config-options {
            margin-top: 30px;
        }
    }
</style>
