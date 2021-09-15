<template>
  <div class="custom-tree-select-container">
    <bk-popover
      ref="popover"
      theme="light custom-tree-select"
      trigger="click"
      animation="slide-toggle"
      :placement="placement"
      :offset="0"
      :distance="12"
      :on-show="handleDropdownShow"
      :on-hide="handleDropdownHide">
      <div
        ref="triggerRef"
        class="custom-tree-select-trigger"
        :class="{ 'active': showDropdown, 'is-not-selected': !selectedName }"
        v-test="'treeSelect'">
        <span v-if="selectedName">{{ selectedName }}</span>
        <span v-else class="holder-text">{{ $t('请选择进程实例') }}</span>
        <span
          v-if="!showDropdown && !selectedName"
          v-bk-tooltips="noSelectedTips"
          class="bk-icon icon-exclamation-circle-shape">
        </span>
        <span class="bk-icon icon-angle-down"></span>
      </div>
      <div slot="content" ref="contentRef" class="custom-tree-select-content" :style="contentStyle">
        <div class="input-container">
          <span class="bk-icon icon-search"></span>
          <input
            v-test="'searchInstance'"
            v-model.trim="searchKeyword"
            ref="searchInput"
            type="text"
            class="search-input"
            :placeholder="$t('请输入关键字')"
            @input="handleSearch">
        </div>
        <div v-bkloading="{ isLoading: searchLoading, opacity: .1 }" class="tree-container">
          <Tree :node-list="treeData" @checked="handleCheckNode" />
        </div>
      </div>
    </bk-popover>
  </div>
</template>

<script>
import Tree from './Tree';
import { clamp } from '@/common/util';

export default {
  components: {
    Tree,
  },
  props: {
    treeData: {
      type: Array,
      default() {
        return [];
      },
    },
    placement: {
      type: String,
      default: 'bottom-start',
    },
    popoverMinWidth: {
      type: Number,
      default: 0,
    },
  },
  data() {
    return {
      selectedName: '',
      noSelectedTips: {
        content: this.$t('预览必须选择实例进程'),
        distance: 20,
      },
      showDropdown: false,
      searchKeyword: '',
      searchLoading: false,
      searchTimer: null,
    };
  },
  computed: {
    contentStyle() {
      return this.popoverMinWidth ? { minWidth: `${this.popoverMinWidth}px` } : {};
    },
  },
  methods: {
    handleDropdownShow() {
      this.showDropdown = true;
      const triggerWidth = this.$refs.triggerRef.getBoundingClientRect().width;
      this.$refs.contentRef.style.width = `${clamp(triggerWidth, 280, 400) - 2}px`;
      this.$nextTick(() => {
        this.$refs.searchInput.focus();
      });
    },
    handleDropdownHide() {
      this.showDropdown = false;
    },

    // 树选择
    handleCheckNode(topoNode) {
      this.setNodeChecked(topoNode, this.treeData);
      this.selectedName = topoNode.topoName;
      this.$emit('selected', topoNode);
      this.$refs.popover.instance.hide();
    },
    // 设置选中叶子节点 checked 为 true，其他为 false
    setNodeChecked(checkedNode, nodeList) {
      nodeList.forEach((topoNode) => {
        topoNode.topoChecked = topoNode === checkedNode;
        if (topoNode.child && topoNode.child.length) {
          this.setNodeChecked(checkedNode, topoNode.child);
        }
      });
    },

    // 树搜索
    handleSearch() {
      this.searchLoading = true;
      this.searchTimer && clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => {
        this.searchTree(this.treeData, this.searchKeyword);
        this.searchLoading = false;
      }, 300);
    },
    searchTree(list, keyword) {
      list.forEach((item) => {
        item.topoExpand = false;
        const isMatched = item.topoName.includes(keyword);
        item.topoVisible = isMatched;
        if (isMatched) {
          this.setParentVisible(item.topoParent, keyword);
        }
        if (item.child && item.child.length) {
          this.searchTree(item.child, keyword);
        }
      });
    },
    setParentVisible(node, keyword) {
      if (node) {
        node.topoVisible = true;
        node.topoExpand = Boolean(keyword);
        this.setParentVisible(node.topoParent, keyword);
      }
    },
  },
};
</script>

<style scoped lang="postcss">
  @import '../../../../../../css/variable.css';
  @import '../../../../../../css/mixins/scroll.css';

  .custom-tree-select-container {
    width: 100%;
    max-width: 400px;
    margin: 0 10px 0 10px;

    /deep/ .bk-tooltip {
      width: 100%;

      .bk-tooltip-ref {
        width: 100%;
      }
    }

    .custom-tree-select-trigger {
      position: relative;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0 4px 0 10px;
      width: 100%;
      height: 32px;
      line-height: 16px;
      border-radius: 2px;
      cursor: pointer;
      font-size: 12px;
      color: $blackThemeColor;
      border: 1px solid $blackThemeBorderColor;
      background-color: $blackThemeBackgroundColor;
      transition: color .2s, border-color .2s, box-shadow .2s;

      .holder-text {
        color: $newBlackColor2;
      }

      .icon-angle-down {
        color: $newBlackColor3;
        font-size: 20px;
        transition: transform .2s;
      }

      .icon-exclamation-circle-shape {
        position: absolute;
        top: 1px;
        right: 30px;
        font-size: 17px;
        color: $newRedColor;
        line-height: 30px;
      }

      &.is-not-selected {
        border-color: #d2332b;
      }

      &:hover {
        color: $blackThemeHoverColor;
        border-color: $blackThemeHoverBorderColor;
        transition: color .2s, border-color .2s;
      }

      &.active {
        border-color: $newMainColor;
        transition: border-color .2s;

        .icon-angle-down {
          transform: rotate(-180deg);
          transition: transform .2s;
        }
      }
    }
  }

  .custom-tree-select-content {
    padding-top: 6px;

    .input-container {
      display: flex;
      align-items: center;
      height: 32px;
      margin: 0 10px;
      border-bottom: 1px solid $newBlackColor2;

      .icon-search {
        flex-shrink: 0;
        font-size: 16px;
        color: $newBlackColor2;
        margin: 0 4px 0 5px;
      }

      .search-input {
        width: 100%;
        border: 0;
        color: $blackThemeColor;
        background-color: #383838;

        &::placeholder {
          padding-left: 2px;
          color: $newBlackColor2;
        }
      }
    }

    .tree-container {
      min-height: 42px;
      max-height: 294px;
      padding-bottom: 6px;
      overflow: auto;

      @mixin scroller 6px, 3px, $newBlackColor2;
    }
  }
</style>

<style lang="postcss">
  @import '../../../../../../css/variable.css';

  .tippy-tooltip.custom-tree-select-theme {
    max-height: 334px;
    padding: 0;
    background: #383838;
    border: 1px solid #474747;
    border-radius: 2px;
    box-shadow: 0 2px 4px 0 rgba(0, 0, 0, .5);

    .tippy-arrow {
      display: none;
    }
  }
</style>
