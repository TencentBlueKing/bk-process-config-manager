<template>
    <ul class="bind-topo-tree">
        <template v-for="(topoNode, index) in nodeList">
            <li v-show="topoNode.topoVisible" class="tree-node-container" :key="index">
                <div :class="['tree-node-item', { 'topo-active': topoNode.topoActive }]"
                    :style="{ 'padding-left': (26 * topoNode.topoLevel) + 'px' }"
                    @click="handleClickNode(topoNode)">
                    <template>
                        <span v-if="['set', 'module'].includes(topoNode.topoType)" :class="['bk-icon icon-right-shape', topoNode.topoExpand && 'expanded']"></span>
                        <!-- 集群 -->
                        <span v-if="topoNode.topoType === 'set'" class="word-icon">{{ $t('集') }}</span>
                        <!-- 服务模板 -->
                        <span
                            v-else-if="topoNode.topoType === 'serviceTemplate'"
                            :style="{ 'margin-left': 26 * (topoNode.topoLevel + 1) - 16 + 'px' }"
                            class="word-icon blue">
                            {{ $t('模') }}
                        </span>
                        <!-- 模块 -->
                        <span v-else-if="topoNode.topoType === 'module'" class="word-icon">{{ $t('模') }}</span>
                        <!-- 服务实例 -->
                        <span
                            v-else-if="topoNode.topoType === 'serviceInstance'"
                            :style="{ 'margin-left': 26 * topoNode.topoLevel - 16 + 'px' }"
                            class="word-icon">
                            {{ $t('实') }}
                        </span>

                        <span v-bk-overflow-tips class="text-content">{{ topoNode.topoName }}</span>
                    </template>
                </div>

                <div v-if="topoNode.topoLoading" class="tree-node-loading"
                    :style="{ 'padding-left': 26 * (topoNode.topoLevel + 1) + 22 + 'px' }">
                    <svg class="svg-icon" aria-hidden="true">
                        <use xlink:href="#gsekit-icon-loading"></use>
                    </svg>
                    <span class="loading-text">{{ $t('加载中') }}</span>
                </div>

                <TopoTree v-if="topoNode.child && topoNode.child.length"
                    v-show="topoNode.topoExpand"
                    :node-list="topoNode.child"
                    :node-reload="topoNode.nodeReload || nodeReload"
                    @selected="handleSelected" />

                <div v-else-if="topoNode.topoExpand && topoNode.topoloaded && topoNode.empty" class="tree-node-empty"
                    :style="{ 'padding-left': 26 * (topoNode.topoLevel + 1) + 22 + 'px' }">
                    {{ topoNode.emptyText || $t('暂无服务实例') }}
                </div>
            </li>
        </template>
        <div class="not-topo" v-if="!nodeList.length">{{ $t('暂无业务拓扑数据') }}</div>
    </ul>
</template>

<script>
    export default {
        name: 'TopoTree',
        props: {
            nodeList: {
                type: Array,
                required: true
            },
            // 节点是否需要重新loading
            nodeReload: {
                type: Boolean,
                default: false
            }
        },
        data () {
            return {
            }
        },
        methods: {
            async handleClickNode (topoNode) {
                topoNode.topoExpand = !topoNode.topoExpand
                const needReload = !topoNode.topoloaded || (topoNode.nodeReload || this.nodeReload)
                if (topoNode.topoExpand && needReload && !(topoNode.child && topoNode.child.length)) {
                    try {
                        topoNode.topoLoading = true
                        if (topoNode.topoType === 'module') {
                            // 需要展开的模块没有服务实例子节点，根据模块查询服务实例列表
                            const res = await this.$store.dispatch('cmdb/ajaxGetServiceListByModule', {
                                data: {
                                    bk_module_ids: [topoNode.bk_inst_id]
                                }
                            })
                            res.data.forEach(item => {
                                item.topoParent = topoNode
                                item.topoVisible = true
                                item.topoExpand = false
                                item.topoLoading = false
                                item.topoActive = false
                                item.topoLevel = topoNode.topoLevel + 1
                                item.topoName = item.service_instance_name
                                item.topoReduceName = topoNode.topoReduceName + item.topoName
                                item.topoType = 'serviceInstance'
                            })
                            topoNode.child = res.data
                            topoNode.topoloaded = true
                        }
                    } catch (e) {
                        console.warn(e)
                    } finally {
                        topoNode.topoLoading = false
                    }
                } else if (topoNode.child && topoNode.child.length) {
                    topoNode.child.forEach(node => {
                        node.topoVisible = true
                    })
                }
                this.$emit('selected', topoNode)
                // topoNode.topoActive = true
            },
            handleSelected (topoNode) {
                this.$emit('selected', topoNode)
            }
        }
    }
</script>

<style lang="postcss" scoped>
    @import "../../../css/variable.css";
    .bind-topo-tree {
        width: 100%;
        .tree-node-container {
            .tree-node-item {
                display: flex;
                align-items: center;
                height: 36px;
                line-height: 20px;
                font-size: 14px;
                color: $newBlackColor2;
                cursor: pointer;
                transition: background-color .2s;
                &:hover {
                    background-color: #e1ecff;
                    transition: background-color .2s;
                }
                .icon-right-shape {
                    margin-left: 16px;
                    flex-shrink: 0;
                    font-size: 14px;
                    color: #c3c6cc;
                    cursor: pointer;
                    margin-right: 6px;
                    transition: transform .2s;
                    &.expanded {
                        transform: rotate(90deg);
                        transition: transform .2s;
                    }
                }
                .word-icon {
                    flex-shrink: 0;
                    width: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #fff;
                    background-color: #c4c6cc;
                    border-radius: 50%;
                    margin-right: 7px;
                    &.blue {
                        background-color: #97aed6;
                    }
                }
                .text-content {
                    width: 100%;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                }
            }
            .topo-active {
                background: #e1ecff;
                color: #3a84ff;
                .word-icon {
                    background-color: #3a84ff !important;
                }
            }
            .tree-node-loading {
                display: flex;
                align-items: center;
                width: 100%;
                height: 36px;
                animation: tree-opacity .3s;
                .svg-icon {
                    width: 16px;
                    height: 16px;
                }
                .loading-text {
                    font-size: 12px;
                    padding-left: 4px;
                    color: #a3c5fd;
                }
                @keyframes tree-opacity {
                    0% {height: 0;opacity: 0;}
                    100% {opacity: 1;height: 36px;}
                }
            }
            .tree-node-empty {
                height: 32px;
                line-height: 32px;
                font-size: 12px;
                color: #979ba5;
            }
        }
        .not-topo {
            height: 100%;
            width: 100%;
            color: #63656e;
            display: flex;
            align-items: center;
            justify-content: center;
        }
    }
</style>
