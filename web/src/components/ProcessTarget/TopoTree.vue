<template>
  <TopoTreeItem
    v-bkloading="{ isLoading: loading, zIndex: 0 }"
    v-bind="$attrs"
    v-on="$listeners"
    :node-list="nodeList"
    @click="handleClick"
    @selected="handleSelected"
    @toggle-check="handleToggleCheck"
    @toggle-expand="handleToggleExpand"
    @load-child="handleLoadChild">
  </TopoTreeItem>
</template>

<script>
import { sortByCustom } from '@/common/util';
import TopoTreeItem from './TopoTreeItem';

export default {
  name: 'TopoTree',
  components: {
    TopoTreeItem,
  },
  props: {
    loading: {
      type: Boolean,
      default: false,
    },
    data: {
      type: Array,
      required: true,
    },
    expandType: {
      type: Array,
      default: () => ['biz', 'set', 'module'],
      // default: () => ['set', 'module', 'serviceTemplate']
      // default: () => ['set', 'module', 'serviceTemplate', 'serviceInstance'] // select
    },
    loadType: {
      type: Array,
      default: () => ['set', 'module', 'serviceTemplate'],
    },
    checkType: {
      type: Array,
      default: () => ['instanceProcess'],
    },
    selectType: {
      type: Array,
      default: () => ['biz', 'set', 'module', 'serviceTemplate', 'instance', 'serviceInstance', 'process'],
    },
    loadChild: {
      type: Function,
      default: null,
    },
  },
  data() {
    return {
      nodeList: [],
    };
  },
  watch: {
    data(value) {
      const copyData = this.formatTopoData(value);
      this.nodeList = copyData.sort(sortByCustom('bk_inst_name'));
      this.$emit('format-tree', this.nodeList);
    },
  },
  methods: {
    handleClick(node) {
      if (node.loading) {
        return;
      }
      // 勾选 - 业务挂钩，可勾选的不能展开。
      if (node.topoProcess) {
        this.handleToggleCheck(node);
        // return
      }
      // 收展
      if (node.ableExpand) {
        this.handleToggleExpand(node);
      }
      // 选中
      if (node.ableSelect) {
        this.handleSelected(node);
      }
      // 加载子节点
      if (node.loadChild && node.topoExpand && !(node.child && node.child.length)) {
        this.handleLoadChild(node);
        return;
      }
      if (node.ableSelect) {
        this.$emit('selected', node);
      }
      this.$emit('click', node);
    },
    async handleLoadChild(node) {
      let loaded = false;
      if (this.loadChild) {
        const childList = await this.loadChild();
        node.child = this.formatTopoData(childList, node.topoLevel, node);
        loaded = true;
      } else {
        try {
          node.topoLoading = true;
          if (node.topoType === 'module') {
            // 需要展开的模块没有服务实例子节点，根据模块查询服务实例列表
            const res = await this.$store.dispatch('cmdb/ajaxGetServiceListByModule', {
              data: {
                bk_module_ids: [node.bk_inst_id],
              },
            });
            res.data.forEach((item) => {
              // item.bk_inst_name = item.service_instance_name
              item.topoType = 'serviceInstance'; // 待确认用途
            });
            node.child = this.formatTopoData(res.data, node.topoLevel, node);
            node.topoloaded = true;
          }
        } catch (e) {
          console.warn(e);
        } finally {
          loaded = true;
          node.topoLoading = false;
        }
      }
      if (loaded) {
        if (node.ableSelect) {
          this.$emit('selected', node);
        }
        this.$emit('click', node);
      }
    },
    // 选中事件
    handleSelected(node) {
      this.setTopoActive(this.nodeList, node.uuid);
    },
    // 勾选事件
    handleToggleCheck(node) {
      console.log(node.topoChecked);
      this.$emit('toggle-check', node);
    },
    handleToggleExpand(node) {
      node.topoExpand = !node.topoExpand;
      this.$emit('toggle-expand', node);
    },
    handleSearch(keyword) {
      this.setNodesVisible(this.nodeList, keyword);
    },
    setNodesVisible(list, keyword) {
      list.forEach((node) => {
        node.topoExpand = false;
        const isMatched = node.topoName.includes(keyword);
        node.topoVisible = isMatched;
        if (isMatched) {
          this.setFilterExpand(node.topoParent, keyword);
        }
        if (node.child && node.child.length) {
          this.setNodesVisible(node.child, keyword);
        }
      });
    },
    setFilterExpand(node, keyword) {
      if (node) {
        node.topoVisible = true;
        node.topoExpand = Boolean(keyword);
        this.setFilterExpand(node.topoParent, keyword);
      }
    },
    formatTopoData(data, topoLevel = -1, parent = null) {
      topoLevel += 1;
      const copyData = [];
      data.reduce((nodeList, item) => {
        const nodeItem = {
          ...item,
          uuid: this.uuid(),
          topoLoading: false,
          topoParent: parent,
          topoVisible: true,
          topoActive: false,
          topoExpand: false,
          topoLevel,
          topoName: item.bk_inst_name || item.service_instance_name,
          topoReduceName: parent && parent.id ? parent.topoReduceName + item.topoName : item.topoName,
          topoProcess: parent && ['serviceInstance', 'instance'].includes(parent.topoType), // 可优化 this.transNodeValue(item, this.checkType)
          topoChecked: false,
          // topoTotalCount: 888
        };
        if (item.bk_obj_id === 'biz') {
          nodeItem.topoType = 'biz';
        } else if (item.bk_obj_id === 'set') {
          nodeItem.topoType = 'set'; // 集群
        } else if (item.bk_obj_id === 'module') {
          nodeItem.empty = true;
          nodeItem.topoloaded = false;
          if (item.service_template_id) { // 服务模板
            nodeItem.topoType = 'serviceTemplate';
          } else { // 模块
            nodeItem.topoType = 'module';
          }
        }
        nodeItem.ableSelect = this.transNodeValue(nodeItem, this.selectType);
        nodeItem.ableExpand = this.transNodeValue(nodeItem, this.expandType);
        nodeItem.loadChild = this.transNodeValue(nodeItem, this.loadType);
        nodeItem.topoConcatPath = parent && parent.uuid ? `${parent.topoConcatPath} / ${nodeItem.topoName}` : nodeItem.topoName;
        if (item.child && item.child.length) {
          nodeItem.child = this.formatTopoData(item.child, topoLevel, nodeItem);
        }
        nodeList.push(nodeItem);
        return nodeList;
      }, copyData);
      return copyData;
    },
    transNodeValue(node, condition) {
      return condition && condition.length ? condition.includes(node.topoType) : true;
    },
    setTopoActive(data, uuid) {
      (data || this.nodeList).forEach((item) => {
        item.topoActive = item.uuid === uuid;
        if (item.topoActive) {
          this.setParentExpand(item.topoParent);
        }
        if (item.child && item.child.length) {
          this.setTopoActive(item.child, uuid);
        }
      });
    },
    setParentExpand(node) {
      if (node) {
        node.topoVisible = true;
        node.topoExpand = true;
        this.setParentExpand(node.topoParent);
      }
    },
    // 取消业务拓扑点击状态
    cancelTopoActive(data) {
      this.setTopoActive(data || this.nodeList);
    },
    getTreeData() {
      return this.nodeList;
    },
    // 获取唯一随机
    uuid() {
      let id = '';
      const randomNum = Math.floor((1 + Math.random()) * 0x10000).toString(16)
        .substring(1);
      for (let i = 0; i < 7; i++) {
        id += randomNum;
      }
      return id;
    },
  },
};
</script>
