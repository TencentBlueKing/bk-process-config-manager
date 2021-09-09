<template>
  <ul class="bind-topo-tree">
    <template v-for="(topoNode, index) in nodeList">
      <li v-show="topoNode.topoVisible" class="tree-node-container" :key="index">
        <div class="tree-node-item" @click="handleClickNode(topoNode)">
          <!-- 进程模板 templateProcess、进程实例 instanceProcess -->
          <template v-if="topoNode.topoProcess">
            <!-- 勾选进程 -->
            <bk-checkbox
              v-model="topoNode.topoChecked" class="king-checkbox"
              :style="{ 'padding-left': 26 * topoNode.topoLevel + 22 + 'px' }"
              @change="handleCheckNode(topoNode)">
              <!-- todo v-bk-overflow-tips -->
              <div class="text-content">{{ topoNode.topoName }}</div>
            </bk-checkbox>
          </template>
          <!-- 1集群、2服务模板、2模块3服务实例 -->
          <template v-else>
            <span :class="['bk-icon icon-right-shape', topoNode.topoExpand && 'expanded']"
                  :style="{ 'margin-left': 26 * topoNode.topoLevel + 'px' }"></span>

            <!-- 集群 -->
            <span v-if="topoNode.topoType === 'set'" class="word-icon">{{ $t('集') }}</span>
            <!-- 服务模板 -->
            <span v-else-if="topoNode.topoType === 'serviceTemplate'" class="word-icon blue">{{ $t('模') }}</span>
            <!-- 模块 -->
            <span v-else-if="topoNode.topoType === 'module'" class="word-icon">{{ $t('模') }}</span>
            <!-- 服务实例 -->
            <span v-else-if="topoNode.topoType === 'serviceInstance'" class="word-icon">{{ $t('实') }}</span>

            <span v-bk-overflow-tips class="text-content">{{ topoNode.topoName }}</span>

            <span v-if="topoNode.topoProcessCount !== undefined" class="process-count">
              {{ topoNode.topoProcessCount }}
            </span>
          </template>
        </div>

        <div
          v-if="topoNode.topoLoading" class="tree-node-loading"
          :style="{ 'padding-left': 26 * (topoNode.topoLevel + 1) + 22 + 'px' }">
          <svg class="svg-icon" aria-hidden="true">
            <use xlink:href="#gsekit-icon-loading"></use>
          </svg>
          <span class="loading-text">{{ $t('加载中') }}</span>
        </div>

        <TopoTree
          v-if="topoNode.child && topoNode.child.length"
          v-show="topoNode.topoExpand"
          :node-list="topoNode.child"
          :template-process="templateProcess"
          :instance-process="instanceProcess"
          @checked="handleCheckNode" />
      </li>
    </template>
  </ul>
</template>

<script>
export default {
  name: 'TopoTree',
  props: {
    nodeList: {
      type: Array,
      required: true,
    },
    templateProcess: {
      type: Array,
      required: true,
    },
    instanceProcess: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {};
  },
  methods: {
    async handleClickNode(topoNode) {
      if (!topoNode.topoProcess) {
        topoNode.topoExpand = !topoNode.topoExpand;
        if (topoNode.topoExpand && !(topoNode.child && topoNode.child.length)) {
          try {
            topoNode.topoLoading = true;
            if (topoNode.topoType === 'module') {
              // 需要展开的模块没有服务实例子节点，根据模块查询服务实例列表
              const res = await this.$store.dispatch('cmdb/ajaxGetServiceListByModule', {
                withProcCount: true,
                data: {
                  bk_module_ids: [topoNode.bk_inst_id],
                },
              });
              res.data.forEach((item) => {
                item.child = [];
                item.topoParent = topoNode;
                item.topoVisible = true;
                item.topoExpand = false;
                item.topoLoading = false;
                item.topoLevel = topoNode.topoLevel + 1;
                item.topoName = item.service_instance_name;
                item.topoProcessCount = item.process_count;
                item.topoReduceName = `${topoNode.topoReduceName}/${item.topoName}`;
                item.topoProcess = false;
                item.topoType = 'serviceInstance';
              });
              topoNode.child = res.data;
            } else if (topoNode.topoType === 'serviceInstance') {
              // 需要展开的服务实例没有实例进程子节点，根据服务实例查询实例进程列表
              const res = await this.$store.dispatch('process/ajaxGetInstanceProcessByServiceInstance', {
                serviceInstanceId: topoNode.service_instance_id, // 2000000174 demo
              });
              res.data.forEach((item) => {
                item.topoParent = topoNode;
                item.topoVisible = true;
                item.topoExpand = false;
                item.topoLoading = false;
                item.topoLevel = topoNode.topoLevel + 1;
                item.topoName = item.property.bk_process_name;
                // 实例进程需要显示父级节点名称
                item.topoReduceName = topoNode.topoReduceName;
                item.topoProcess = true;
                item.topoType = 'instanceProcess';
                item.topoChecked = false;
                // 替换回填的进程对象
                let findItem; let findIndex;
                for (let i = 0; i < this.instanceProcess.length; i++) {
                  const selectedItem = this.instanceProcess[i];
                  if (selectedItem.__IS_RECOVER
                    && selectedItem.property.bk_process_id === item.property.bk_process_id) {
                    findItem = selectedItem;
                    findIndex = i;
                    break;
                  }
                }
                if (findItem) {
                  item.topoChecked = true;
                  const copyProcess = [...this.instanceProcess];
                  copyProcess.splice(findIndex, 1, item);
                  this.$emit('update:instanceProcess', copyProcess);
                }
              });
              topoNode.child = res.data;
            } else if (topoNode.topoType === 'serviceTemplate') {
              // 需要展开的服务模板没有模板进程子节点，根据服务模板查询模板进程列表
              const res = await this.$store.dispatch('process/ajaxGetTemplateProcessByServiceTemplate', {
                // topo里面的服务模板使用 service_template_id，直接拉取的服务模板列表使用 id
                serviceTemplateId: topoNode.service_template_id || topoNode.id,
              });
              res.data.forEach((item) => {
                item.topoParent = topoNode;
                item.topoVisible = true;
                item.topoExpand = false;
                item.topoLoading = false;
                item.topoLevel = topoNode.topoLevel + 1;
                item.topoName = item.bk_process_name;
                // 模板进程需要显示模板名称
                item.topoTemplateName = topoNode.topoName;
                item.topoProcess = true;
                item.topoType = 'templateProcess';
                item.topoChecked = false;
                // 替换回填的进程对象
                let findItem; let findIndex;
                for (let i = 0; i < this.templateProcess.length; i++) {
                  const selectedItem = this.templateProcess[i];
                  if (selectedItem.__IS_RECOVER && selectedItem.id === item.id) {
                    findItem = selectedItem;
                    findIndex = i;
                    break;
                  }
                }
                if (findItem) {
                  item.topoChecked = true;
                  const copyProcess = [...this.templateProcess];
                  copyProcess.splice(findIndex, 1, item);
                  this.$emit('update:templateProcess', copyProcess);
                }
              });
              topoNode.child = res.data;
            }
          } catch (e) {
            console.warn(e);
          } finally {
            topoNode.topoLoading = false;
          }
        } else if (topoNode.child && topoNode.child.length) {
          topoNode.child.forEach((node) => {
            node.topoVisible = true;
          });
        }
      }
    },
    handleCheckNode(topoNode) {
      this.$emit('checked', topoNode);
    },
  },
};
</script>

<style scoped lang="postcss">
  @import '../../../../../css/variable.css';

  .bind-topo-tree {
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
          background-color: #f0f1f5;
          transition: background-color .2s;
        }

        .icon-right-shape {
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

        .process-count {
          flex-shrink: 0;
          padding: 0 2px;
          min-width: 16px;
          line-height: 16px;
          text-align: center;
          font-size: 12px;
          color: $newBlackColor3;
          background: #f0f1f5;
          border-radius: 2px;
        }

        .king-checkbox {
          display: flex;
          align-items: center;
          width: 100%;
          height: 100%;

          /deep/ .bk-checkbox {
            flex-shrink: 0;
          }

          /deep/ .bk-checkbox-text {
            margin-left: 8px;
            width: calc(100% - 24px);
          }
        }
      }

      .tree-node-loading {
        display: flex;
        align-items: center;
        width: 100%;
        height: 36px;
        animation: tree-opacity .3s;

        @keyframes tree-opacity {
          0% {
            height: 0;opacity: 0;
          }

          100% {
            opacity: 1;height: 36px;
          }
        }

        .svg-icon {
          width: 16px;
          height: 16px;
        }

        .loading-text {
          font-size: 12px;
          padding-left: 4px;
          color: #a3c5fd;
        }
      }
    }
  }
</style>
