<template>
  <ul class="select-tree-container">
    <template v-for="(topoNode, index) in nodeList">
      <li v-show="topoNode.topoVisible" class="tree-node-container" :key="index">
        <div
          class="tree-node-item"
          :class="{ 'checked-node-item': topoNode.topoChecked }"
          :style="{ 'padding-left': 8 + 30 * topoNode.topoLevel + 'px' }"
          @click="handleClickNode(topoNode)">
          <!-- 非进程，即非叶子节点，有展开或加载图标 -->
          <div v-if="!topoNode.topoProcess" class="icon-container">
            <svg v-if="topoNode.topoLoading" class="svg-icon" aria-hidden="true">
              <use xlink:href="#gsekit-icon-loading"></use>
            </svg>
            <span v-else :class="['bk-icon icon-right-shape', topoNode.topoExpand && 'expanded']"></span>
          </div>
          <div class="node-type-icon" :class="{ 'process-type': topoNode.topoProcess }">
            {{ nodeTypeMap[topoNode.topoLevel] }}
          </div>
          <div v-bk-overflow-tips class="text-content">
            {{ topoNode.topoName }}
          </div>
          <div v-if="topoNode.topoType === 'instanceProcess' && topoNode.unmanaged" class="node-tag process-unmanaged">
            {{ $t('未关联') }}
          </div>
          <div v-if="topoNode.topoProcessCount !== undefined" class="node-tag process-count">
            {{ topoNode.topoProcessCount }}
          </div>
        </div>

        <Tree
          v-if="topoNode.child && topoNode.child.length"
          v-show="topoNode.topoExpand"
          :node-list="topoNode.child"
          @checked="handleCheckNode" />
      </li>
    </template>
  </ul>
</template>

<script>
export default {
  name: 'Tree',
  inject: ['linkedProcess'],
  props: {
    nodeList: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      nodeTypeMap: [this.$t('集'), this.$t('模'), this.$t('实'), this.$t('进')],
    };
  },
  computed: {
    linkedList() {
      return this.linkedProcess();
    },
  },
  methods: {
    async handleClickNode(topoNode) {
      if (topoNode.topoProcess) { // 点击了进程节点
        this.$emit('checked', topoNode);
      } else {
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
                item.topoProcess = true;
                item.topoType = 'instanceProcess';
                item.topoChecked = false;
                item.unmanaged = !this.linkedList.find(({ type, id }) => (type === 'TEMPLATE' ? id === item.process_template_id : id === item.bk_process_id));
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
  @import '../../../../../../css/variable.css';

  .select-tree-container {
    .tree-node-container {
      .tree-node-item {
        display: flex;
        align-items: center;
        height: 36px;
        line-height: 20px;
        padding-right: 8px;
        font-size: 14px;
        cursor: pointer;
        color: $newBlackColor3;
        transition: color .2s, background-color .2s;

        .icon-container {
          flex-shrink: 0;
          display: flex;
          justify-content: center;
          align-items: center;
          width: 20px;
          height: 20px;
          margin-right: 4px;

          .icon-right-shape {
            font-size: 14px;
            cursor: pointer;
            color: $newBlackColor2;
            transition: color .2s, transform .2s;

            &.expanded {
              transform: rotate(90deg);
              transition: transform .2s;
            }
          }

          .svg-icon {
            width: 14px;
            height: 14px;
          }
        }

        .node-type-icon {
          flex-shrink: 0;
          width: 18px;
          height: 18px;
          line-height: 18px;
          margin-right: 6px;
          text-align: center;
          border-radius: 9px;
          overflow: hidden;
          font-size: 12px;
          color: #383838;
          background-color: #c4c6cc;

          &.process-type {
            margin-left: 24px;
          }
        }

        .text-content {
          width: 100%;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .node-tag {
          flex-shrink: 0;
          padding: 0 2px;
          min-width: 16px;
          line-height: 16px;
          text-align: center;
          font-size: 12px;
          border-radius: 2px;
          color: $newBlackColor3;
          background: #474747;
        }

        .process-unmanaged {
          padding: 0 6px;
          color: #ad4d3e;
          background: #412525;
        }

        &:hover {
          color: #e1ecff;
          background-color: #415782;
          transition: color .2s, background-color .2s;

          .icon-right-shape {
            color: $newBlackColor3;
            transition: color .2s;
          }

          .node-type-icon {
            background-color: #e1ecff;
          }
        }

        &.checked-node-item {
          color: #e1ecff;
          background-color: #346;
          transition: color .2s, background-color .2s;

          .icon-right-shape {
            color: $newBlackColor3;
            transition: color;
          }

          .node-type-icon {
            background-color: #fff;
          }
        }
      }
    }
  }
</style>
