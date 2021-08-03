<template>
  <ul class="topo-tree">
    <li
      class="tree-node-container"
      v-for="(node,index) in nodeList"
      v-show="node.topoVisible"
      :key="index">
      <div
        :class="['tree-node-item', { 'topo-active': node.topoActive }]"
        :style="{ 'padding-left': (26 * node.topoLevel) + 'px' }"
        @click="handleClickNode(node)">
        <!-- 左侧图标 -->
        <div :class="['node-flex-start', { expanded: node.topoExpand }]">
          <template v-if="node.ableExpand">
            <svg v-if="node.topoLoading && loadPosition === 'left'" class="svg-icon" aria-hidden="true">
              <use xlink:href="#gsekit-icon-loading"></use>
            </svg>
            <span v-else class="bk-icon icon-right-shape"></span>
          </template>
        </div>
        <!-- 节点类型 -->
        <span v-if="nodeTypeMap[node.topoType]" :class="`word-icon ${ node.topoType }`">
          {{ nodeTypeMap[node.topoType] }}
        </span>
        <!-- 可勾选 -->
        <template v-if="node.topoProcess">
          <!-- 勾选进程 -->
          <bk-checkbox v-model="node.topoChecked" class="king-checkbox">
            <div class="text-content" v-bk-overflow-tips>{{ node.topoName }}</div>
          </bk-checkbox>
        </template>
        <span v-bk-overflow-tips class="node-name" v-else>{{ node.topoName }}</span>
        <div v-if="node.topoTotalCount !== undefined" class="node-total-box">{{ node.topoTotalCount }}</div>
      </div>
      <TopoTreeItem
        v-if="node.topoExpand && node.child && node.child.length"
        v-show="node.topoExpand"
        :node-list="node.child"
        :load-position="loadPosition"
        @click="handleClickNode">
      </TopoTreeItem>
      <div
        v-else-if="loadPosition === 'child' && node.topoExpand"
        :style="{ 'padding-left': 26 * (node.topoLevel + 1) + 22 + 'px' }">
        <div v-if="node.topoLoading" class="tree-node-loading">
          <svg class="svg-icon" aria-hidden="true">
            <use xlink:href="#gsekit-icon-loading"></use>
          </svg>
          <span class="loading-text">{{ $t('加载中') }}</span>
        </div>
        <span v-else-if="!node.topoLoading && node.empty" class="node-child-empty">
          {{ node.emptyText || emptyChildText }}
        </span>
      </div>

      <div v-else-if="node.topoExpand && node.topoloaded && node.empty" class="tree-node-empty"
           :style="{ 'padding-left': 26 * (node.topoLevel + 1) + 22 + 'px' }">
        {{ node.emptyText || emptyChildText }}
      </div>
    </li>
    <slot v-if="!nodeList.length" name="empty">
      <div class="not-topo">{{ $t('暂无业务拓扑数据') }}</div>
    </slot>
  </ul>
</template>

<script>
export default {
  name: 'TopoTreeItem',
  props: {
    nodeList: {
      type: Array,
      required: true,
    },
    // 子节点加载loading位置
    loadPosition: {
      type: String,
      default: 'left', // left && child
    },
    emptyChildText: {
      type: String,
      default: window.i18n.t('暂无服务实例'),
    },
  },
  data() {
    return {
      nodeTypeMap: {
        set: this.$t('集'),
        module: this.$t('模'),
        serviceTemplate: this.$t('模'),
        instance: this.$t('实'),
        serviceInstance: this.$t('实'),
        process: this.$t('进'),
      },
    };
  },
  methods: {
    handleClickNode(node) {
      this.$emit('click', node);
    },
  },
};
</script>

<style lang="postcss" scoped>
  @import '../../css/variable.css';

  .topo-tree {
    width: 100%;

    .tree-node-container {
      .tree-node-item {
        position: relative;
        display: flex;
        align-items: center;
        padding-right: 20px;
        height: 36px;
        line-height: 20px;
        font-size: 14px;
        color: $newBlackColor2;
        cursor: pointer;
        transition: background-color .2s;

        &:hover {
          background-color: #e1ecff;
        }

        &:first-child {
          margin-left: 20px;
        }

        .node-flex-start {
          /* margin-left: 20px; */
          flex-shrink: 0;
          width: 14px;
          height: 14px;
          font-size: 0;
          cursor: pointer;
          transition: transform .2s;

          &.expanded {
            transform: rotate(90deg);
            transition: transform .2s;
          }

          & + .word-icon,
          & + king-checkbox {
            margin-left: 5px;
          }

          & + .node-name {
            margin-left: 7px;
          }
        }

        .icon-right-shape {
          font-size: 14px;
          color: #c3c6cc;
        }

        .svg-icon {
          width: 14px;
          height: 14px;
        }

        .word-icon {
          flex-shrink: 0;
          width: 20px;
          text-align: center;
          font-size: 12px;
          color: #fff;
          background-color: #c4c6cc;
          border-radius: 50%;

          & + .node-name,
          & + .king-checkbox {
            margin-left: 7px;
          }

          &.serviceTemplate {
            background-color: #97aed6;
          }
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

        .node-name {
          flex: 1;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .node-total-box {
          margin-left: 5px;
          padding: 0 5px;
          min-width: 18px;
          line-height: 18px;
          text-align: center;
          font-size: 12px;
          color: $newBlackColor3;
          background: #e8e9ed;
          border-radius: 2px;
        }
      }

      .topo-active {
        background: #e1ecff;
        color: #3a84ff;

        .word-icon {
          background-color: #3a84ff !important;
        }

        .node-total-box {
          color: #fff;
          background: #a3c5fd;
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

      .node-child-empty {
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
