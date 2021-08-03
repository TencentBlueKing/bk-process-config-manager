<template>
  <section>
    <div class="filter-header" :class="{ 'default': filterList.length === 0 }" @click.stop="handleShow($event)">
      {{ name }}
      <i
        class="header-icon gsekit-icon gsekit-icon-filter-fill"
        :class="{ 'is-selected': isSelected }"
        v-if="filterList.length">
      </i>
    </div>
    <!--筛选面板-->
    <div v-show="false">
      <div class="label-menu-wrapper" ref="labelMenu">
        <ul class="label-menu-list" v-if="filterList.length">
          <li
            class="item"
            v-for="(item, index) in currentList"
            :title="item.name"
            :key="index"
            @click="handleSelectLabel(item)">
            <bk-checkbox class="check-box" v-if="isMultipleChoice" :value="item.checked"></bk-checkbox>
            <span class="item-name">{{item.name}}</span>
          </li>
          <li class="item-empty" v-show="!currentList.length">
            {{ $t('无匹配数据') }}
          </li>
        </ul>
        <div class="footer" :style="{ 'justify-content': footerAlign }" v-if="isMultipleChoice && filterList.length">
          <bk-button text @click="handleConfirm" ext-cls="footer-btn mr20">{{ $t('确定') }}</bk-button>
          <bk-button text @click="handleResetSelected" ext-cls="footer-btn">{{ $t('重置') }}</bk-button>
        </div>
      </div>
    </div>
  </section>
</template>
<script>
export default {
  name: 'FilterHeader',
  props: {
    name: {
      type: String,
      default: '',
    },
    filterList: {
      type: Array,
      default: () => [],
    },
    property: {
      type: String,
      default: '',
    },
    isMultipleChoice: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      instance: null,
      list: JSON.parse(JSON.stringify(this.filterList)),
      selectIds: [],
    };
  },
  computed: {
    isSelected() {
      return this.list.some(item => item.checked);
    },
    footerAlign() {
      switch (this.align) {
        case 'center':
          return 'space-between';
        case 'left':
          return 'flex-start';
        case 'right':
          return 'flex-end';
        default:
          return 'space-between';
      }
    },
    currentList() {
      return this.isEmpty(this.searchValue) ? this.list
        : this.list.filter(item => item.name && ~item.name.toString().toLocaleLowerCase()
          .indexOf(this.searchValue.toLocaleLowerCase()));
    },
  },
  watch: {
    filterList: {
      deep: true,
      handler(val) {
        this.list = JSON.parse(JSON.stringify(val));
        this.selectIds = this.list.filter(item => item.checked).map(item => item.id);
      },
    },
  },
  beforeDestroy() {
    this.instance && this.instance.destroy();
    this.instance = null;
  },
  methods: {
    isEmpty(obj) {
      return typeof obj === 'undefined' || obj === null || obj === '';
    },
    handleShow(e) {
      if (!this.filterList.length) return;
      // const target = e.target.tagName === 'SPAN' ? e.target : e.target.parentNode
      if (!this.instance) {
        this.instance = this.$bkPopover(e.target, {
          content: this.$refs.labelMenu,
          trigger: 'click',
          arrow: false,
          placement: 'bottom',
          theme: 'light filter-header',
          maxWidth: 520,
          offset: '0, 0',
          sticky: true,
          duration: [275, 0],
          interactive: true,
          onHidden: () => {
            this.list.forEach((item) => {
              item.checked = this.selectIds.includes(item.id);
            });
            this.instance && this.instance.destroy();
            this.instance = null;
          },
        });
      }
      this.instance && this.instance.show(100);
    },
    handleSelectLabel(item) {
      item.checked = !item.checked;
      if (!this.isMultipleChoice) {
        this.handleConfirm();
      }
    },
    handleConfirm() {
      this.selectIds = this.list.filter(item => item.checked).map(item => item.id);
      if (this.selectIds.length) {
        this.$emit('confirm', this.property, this.list);
      } else {
        this.$emit('reset', this.property);
      }
      this.instance && this.instance.hide(100);
    },
    handleResetSelected() {
      this.selectIds = [];
      this.list.forEach((item) => {
        item.checked = false;
      });
      this.instance && this.instance.hide(100);
      this.$emit('reset', this.property);
    },
  },
};
</script>
<style lang="postcss" scoped>
  @import '../../css/mixins/scroll.css';

  .filter-header {
    cursor: pointer;
    outline: 0;

    &.default {
      cursor: default;
    }

    .header-icon {
      position: relative;
      font-size: 13px;
      color: #c4c6cc;
      outline: 0;
    }

    .is-selected {
      color: #3a84ff;
    }
  }

  .label-menu-wrapper {
    min-width: 100px;

    .label-menu-list {
      max-height: 200px;
      overflow: auto;
      padding: 6px 0;
      background-color: #fff;

      @mixin scroller;

      .item {
        font-size: 12px;
        color: #63656e;
        cursor: pointer;
        padding: 0 10px;
        height: 32px;
        line-height: 32px;

        .check-box {
          overflow: unset;
        }

        &:hover {
          background: #e1ecff;
          color: #3a84ff;
        }

        &-name {
          margin-left: 6px;
          overflow: hidden;
          white-space: nowrap;
          text-overflow: ellipsis;
        }
      }

      .item-empty {
        font-size: 12px;
        text-align: center;
        color: #c4c6cc;
        line-height: 24px;
      }
    }

    .footer {
      padding: 0 15px;
      height: 30px;
      border-top: 2px solid #f0f1f5;
      background-color: #fff;

      &-btn {
        font-size: 12px;
      }
    }
  }
</style>
