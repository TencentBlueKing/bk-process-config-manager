<template>
  <div v-bkloading="{ isLoading: basicLoading, opacity: .1 }" class="version-preview-container">
    <div class="right-panel-header">
      <div class="icon-container" @click="$emit('close')">
        <span class="bk-icon icon-expand-line"></span>
      </div>
      <div class="title">{{ $t('预览') }}</div>
      <div class="head-select">
        <!-- <div class="vertical-line"></div> -->
        <div class="process-instance">
          {{ $t('进程实例') }}
          <span class="star">*</span>
        </div>
        <TreeSelect
          ref="treeSelectRef"
          placement="bottom-end"
          :popover-min-width="398"
          :tree-data="topoData"
          @selected="handleSelected" />
      </div>
    </div>
    <div class="right-panel-main">
      <CodeEditor :content="codeContent" :language="codeLanguage" />
    </div>
  </div>
</template>

<script>
import TreeSelect from './TreeSelect';
import CodeEditor from '@/components/CodeEditor';
import { sortByCustom } from '@/common/util';

export default {
  name: 'VersionPreview',
  components: {
    TreeSelect,
    CodeEditor,
  },
  provide() {
    return {
      linkedProcess: () => this.linkedProcess,
    };
  },
  props: {
    templateId: {
      type: String,
      default: '',
    },
    showPreviewPanel: {
      type: Boolean,
      default: false,
    },
    previewLanguage: {
      type: String,
      default: 'python',
    },
    previewContent: {
      type: String,
      default: '',
    },
    previewContentCache: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      codeContent: '',
      codeLanguage: 'python',
      basicLoading: false,
      topoData: [],
      selectedProcess: null,
      linkedProcess: [],
    };
  },
  watch: {
    showPreviewPanel: {
      handler(val) {
        if (val) {
          if (this.topoData.length) { // 再次打开
            this.handleRefresh();
          } else { // 第一次打开
            this.getProcessList();
            this.getTemplateBindRelationship();
          }
        }
      },
      immediate: true,
    },
  },
  methods: {
    // 获取树选择列表数据
    async getProcessList() {
      try {
        this.basicLoading = true;
        const res = await this.$store.dispatch('cmdb/ajaxGetBizTopo');
        const topoData = res.data.length ? res.data[0].child : [];
        this.filterTopoData(topoData);
        this.topoData = this.getHasProcessTopo(topoData);
        this.$nextTick(this.openSelect);
      } catch (e) {
        console.warn(e);
      } finally {
        this.basicLoading = false;
      }
    },
    async getTemplateBindRelationship() {
      try {
        const { data = [] } = await this.$store.dispatch('configTemplate/ajaxGetTemplateBindRelationship', { templateId: this.templateId });
        this.linkedProcess = data.map(item => ({
          id: item.process_object_id,
          type: item.process_object_type,
        }));
      } catch (e) {
        console.warn(e);
      }
    },
    // 打开下拉列表
    openSelect() {
      this.$refs.treeSelectRef.$el.querySelector('.custom-tree-select-trigger').click();
    },
    // 遍历拓扑树，结构如下：
    // set module serviceInstance process
    // 集群 模块 服务实例 进程
    filterTopoData(topoData, topoLevel = -1, parent = null) {
      topoLevel += 1;
      topoData.sort(sortByCustom('bk_inst_name'));
      topoData.forEach((item) => {
        item.topoParent = parent;
        item.topoVisible = true;
        item.topoExpand = false;
        item.topoLoading = false;
        item.topoLevel = topoLevel;
        item.topoName = item.bk_inst_name;
        item.topoProcessCount = item.process_count;
        item.topoProcess = false; // 是否是进程节点
        item.topoType = item.bk_obj_id; // set module 只有两层数据，后面的数据接口获取
        if (item.child && item.child.length) {
          this.filterTopoData(item.child, topoLevel, item);
        }
      });
    },
    getHasProcessTopo(data) {
      const topo =  data.filter(item => !['set', 'module'].includes(item.topoType) || item.topoProcessCount);
      topo.forEach((item) => {
        if (item.child && item.child.length) {
          item.child = this.getHasProcessTopo(item.child);
        }
      });
      return topo;
    },

    // 树选择事件
    handleSelected(topoNode) {
      this.selectedProcess = topoNode;
      this.handleRefresh();
    },
    // 刷新进程实例，重新获取内容，更新编辑器
    async handleRefresh() {
      if (!this.selectedProcess) {
        this.openSelect();
        return;
      }
      try {
        this.basicLoading = true;
        const res = await this.$store.dispatch('configVersion/ajaxPreviewConfigVersion', {
          data: {
            content: this.previewContent,
            bk_process_id: this.selectedProcess.property.bk_process_id,
          },
        });
        this.codeLanguage = this.previewLanguage;
        this.codeContent = res.data;
        this.$emit('update:previewContentCache', this.previewContent);
        this.$emit('markers', []);
      } catch (e) {
        console.warn(e);
        this.formatMaker(e);
        this.codeContent = '';
      } finally {
        this.basicLoading = false;
      }
    },
    formatMaker(error) {
      const markers = [];
      try {
        const msgReg = /\[.*\]/g;
        let { message } = error;
        if (!message) throw new Error();
        if (msgReg.test(message)) {
          const markMatch = message.match(/\[.*\]/g);
          if (markMatch) {
            const markListStr = markMatch[0].substring(1, markMatch[0].length - 1);
            message = markListStr.replace('，错误：', ' ');
          }
        }
        markers.push({ type: 'msg', message });
      } catch (e) {
        markers.push({ type: 'msg', message: JSON.stringify(error) });
      } finally {
        console.log(markers);
        this.$emit('markers', markers);
      }
    },
  },
};
</script>

<style scoped lang="postcss">
  @import '../../../../../../css/variable.css';

  .version-preview-container {
    display: flex;
    flex-flow: column;
    height: 100%;

    .right-panel-header {
      justify-content: space-between;

      .vertical-line {
        flex-shrink: 0;
        width: 1px;
        height: 16px;
        margin: 0 20px 0 14px;
        background-color: #63656e;
      }

      .head-select {
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        margin-left: 10px;
      }

      .process-instance {
        flex-shrink: 0;
        font-size: 12px;

        .star {
          color: $newRedColor;
        }
      }
    }

    .right-panel-main {
      height: 100%;
    }
  }
</style>
