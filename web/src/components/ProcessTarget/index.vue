<template>
  <div class="process-target">
    <section class="topo-tab">
      <div class="bk-button-group">
        <bk-button
          v-for="tab in tabList" :key="tab.id"
          :theme="tab.id === tabActive ? 'primary' : 'default'"
          @click="handleTabClick(tab)">
          {{ tab.name }}
        </bk-button>
      </div>
    </section>
    <div class="topo-search">
      <bk-input
        v-show="showBizTopo"
        :value="topoSearchKeyword"
        :placeholder="$t('请输入关键字')"
        :right-icon="'bk-icon icon-search'"
        clearable
        @change="handleSearch">
      </bk-input>
      <bk-input
        v-show="!showBizTopo"
        :placeholder="$t('请输入关键字')"
        :right-icon="'bk-icon icon-search'"
        v-model.trim="tempSearchKeyword"
        clearable
        @change="handleSearch">
      </bk-input>
    </div>
    <div v-show="showBizTopo" class="topo-content" v-bkloading="{ isLoading: loading || searchLoading, opacity: 1 }">
      <TopoTree
        ref="topoTree"
        load-position="child"
        :data="treeData"
        node-reload
        @selected="handleTreeSelected"
        @format-tree="handleUpdateTree" />
    </div>
    <div v-show="!showBizTopo" class="topo-content" v-bkloading="{ isLoading: loading || searchLoading, opacity: 0 }">
      <ServerTemplate ref="serverTemp" :search-word="tempSearchKeyword" :list="templateList" @click="handleTempClick" />
    </div>
  </div>
</template>

<script>
import ServerTemplate from './ServerTemplate';
import TopoTree from './TopoTree';
// import { sortByCustom } from '@/common/util'

export default {
  name: 'ProcessTarget',
  components: {
    ServerTemplate,
    TopoTree,
  },
  model: {
    prop: 'tabActive',
    event: 'tab-change',
  },
  props: {
    loading: {
      type: Boolean,
      default: false,
    },
    treeData: {
      type: Array,
      defaut: () => [],
    },
    templateList: {
      type: Array,
      defaut: () => [],
    },
    tabActive: {
      type: String,
      default: 'template',
    },
    timely: {
      type: Boolean,
      default: true,
    },
    debounceTime: {
      type: Number,
      default: 300,
    },
  },
  data() {
    return {
      tabList: [
        { id: 'template', name: window.i18n.t('按服务模板') },
        { id: 'node', name: window.i18n.t('按业务拓扑') },
      ],
      searchLoading: false,
      tempSearchKeyword: '',
      topoSearchKeyword: '',
      searchTimer: null,
    };
  },
  computed: {
    showBizTopo() {
      return this.tabActive === 'node';
    },
  },
  methods: {
    handleTabClick(tab) {
      if (tab !== this.tabActive) {
        if (this.timely) {
          this.handleTimelyChange(tab);
        }
        this.$emit('tab-change', tab.id);
      }
    },
    handleSearch(value) {
      this.searchLoading = true;
      this.searchTimer && clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => {
        if (this.tabActive === 'node') {
          this.topoSearchKeyword = value.trim();
          this.$refs.topoTree.handleSearch(this.topoSearchKeyword);
        } else {
          this.tempSearchKeyword = value.trim();
        }
        this.searchLoading = false;
      }, this.debounceTime);
    },
    handleTempClick(val) {
      this.$refs.topoTree.cancelTopoActive();
      this.$emit('temp-selected', val);
    },
    handleTreeSelected(node) {
      this.$refs.serverTemp.cancelActive();
      this.$emit('tree-selected', node);
    },
    handleUpdateTree(list) {
      this.$emit('format-tree', list);
    },
    handleTimelyChange(type) {
      if (type === 'template') {
        this.topoSearchKeyword = '';
        this.$refs.topoTree.cancelTopoActive();
      } else {
        this.$refs.serverTemp.cancelActive();
        this.tempSearchKeyword = '';
      }
    },
    handleSetTemplateActive(item) {
      this.$refs.serverTemp.setAtive(item);
    },
    handleSetTopoActive(uuid) {
      this.$refs.topoTree.setTopoActive(null, uuid);
    },
  },
};
</script>

<style lang="postcss" scoped>
  @import '../../css/mixins/scroll.css';

  .process-target {
    display: flex;
    flex-direction: column;
    max-height: 100%;
    overflow: hidden;

    .topo-tab {
      margin-bottom: 12px;
      padding: 0 20px;

      .bk-button-group {
        display: flex;

        .bk-button {
          flex: 1;
          padding: 0;

          &.bk-primary {
            position: relative;
            border-radius: 2px;
            border: 1px solid #3a84ff;
            color: #3a84ff;
            background-color: #c7dcff;
            z-index: 4;
          }
        }
      }
    }

    .topo-search {
      margin-bottom: 16px;
      padding: 0 20px;
    }

    .topo-content {
      flex: 1;
      padding: 0;
      margin-bottom: 0;
      max-height: calc(100% - 92px);
      overflow: auto;

      @mixin scroller;
    }
  }
</style>
