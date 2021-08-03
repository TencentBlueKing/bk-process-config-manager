<template>
  <div :class="['bk-cascade', { 'is-focus': showCascade }]">
    <i class="bk-cascade-angle bk-icon icon-angle-down"></i>
    <i class="bk-cascade-clear bk-icon icon-close" @click.prevent.stop="clearData" v-if="selectedName"></i>
    <bk-popover
      style="max-width: 100%;"
      class="bk-cascade-dropdown"
      ref="cascadeDropdown"
      trigger="click"
      :z-index="2"
      :distance="15"
      :offset="-1"
      placement="bottom-start"
      theme="light bk-cascade-dropdown"
      animation="slide-toggle"
      :on-show="handleDropdownShow"
      :on-hide="handleDropdownHide">
      <div :class="['bk-cascade-name', { 'placeholder-text': !selectedName }]" v-bk-overflow-tips>
        <span>{{ selectedName || name }}</span>
      </div>
      <div slot="content" class="bk-cascade-dropdown-content">
        <div class="bk-cascade-panel">
          <ul class="bk-cascade-panel-ul">
            <li
              v-for="item in allSearchData"
              :key="item.id"
              :class="['bk-option', { 'is-selected': isSelectedId === item.id }]"
              @click.prevent.stop="handleSelectItem(item)">
              <span>{{ item.name }}</span>
            </li>
          </ul>
        </div>
        <Caspanel
          :list="selcetData.children"
          :select-id="selectId"
          :environment-id="selcetData.id"
          :name="name"
          @onSearch="onSearch"
          @clickAllSetSelect="onClickAllSetSelect"
          @clickSetSelect="onClickSetSelect">
        </Caspanel>
      </div>
    </bk-popover>
  </div>
</template>

<script>
import Caspanel from './Caspanel';
export default {
  components: {
    Caspanel,
  },
  props: {
    list: {
      type: Array,
      default: () => [],
    },
    value: {
      type: Array,
      default: () => [],
    },
    name: {
      type: String,
      default: '集群',
    },
  },
  data() {
    return {
      allSearchData: [], // 所有数据
      showCascade: false, // 是否获取焦点
      selectedName: '', // 展示内容
      selcetData: {}, // 当前选中的环境数据
      selectId: [], // 当前选中集群的id
      isSelectedId: 'all', // 默认选中第一个环境
      allSetList: [], // 所有集群
    };
  },
  watch: {
    list: {
      handler(val) {
        const allSearchData = JSON.parse(JSON.stringify(val));
        const allSetList = [];
        allSearchData.forEach((item) => {
          if (item.children && item.children.length) {
            allSetList.push(...item.children);
          }
        });
        allSetList.forEach((item) => {
          item.isShow = true;
        });
        allSearchData.unshift({
          id: 'all',
          name: this.$t('全部'),
          children: allSetList,
        });
        this.selcetData = allSearchData[0];
        this.allSearchData = allSearchData;
        this.allSetList = allSetList;
      },
      immediate: true,
    },
    value: {
      handler(val) {
        if (!val.length) {
          this.selectId = [];
          return;
        }
        if (!this.isSame(val, this.selected)) {
          this.selectId = val;
        }
      },
      immediate: true,
    },
    selectId: {
      handler(val) {
        const selectedName = [];
        for (const item of this.allSetList) {
          if (val.includes(item.id)) {
            selectedName.push(item.name);
          }
        }
        this.selectedName = selectedName.join('，');
      },
      immediate: true,
    },
  },
  methods: {
    // popover关闭
    handleDropdownHide() {
      this.showCascade = false;
      this.$emit('change', this.selectId);
      this.$emit('input', this.selectId);
    },
    // popover展示
    handleDropdownShow() {
      this.showCascade = true;
    },
    // 清除数据
    clearData() {
      this.selectedName = '';
      this.selectId = [];
      this.selcetData = this.allSearchData[0];
      this.isSelectedId = 'all';
      this.$emit('change', this.selectId);
      this.$emit('input', this.selectId);
    },
    // 选择环境
    handleSelectItem(val) {
      this.isSelectedId = val.id;
      this.selcetData = val;
    },
    // 关闭tippy
    tippyInstance() {
      if (this.$refs.cascadeDropdown) {
        this.$refs.cascadeDropdown.$refs.reference._tippy.hide();
      }
    },
    // 全部集群
    onClickAllSetSelect() {
      if (this.selcetData.id === 'all') {
        this.selectId = [];
        return;
      }
      // isCheckAll 当前是否全选
      let isCheckAll = true;
      this.selcetData.children.forEach((item) => {
        if (!this.selectId.includes(item.id)) {
          isCheckAll = false;
        }
      });
      // 全选
      if (!isCheckAll) {
        this.selcetData.children.forEach((item) => {
          if (!this.selectId.includes(item.id)) {
            this.selectId.push(item.id);
          }
        });
      } else { // 全不选
        this.selcetData.children.forEach((item) => {
          const index = this.selectId.findIndex(val => item.id === val);
          this.selectId.splice(index, 1);
        });
      }
    },
    // 单个集群
    onClickSetSelect(val) {
      const index = this.selectId.findIndex(item => val.id === item);
      if (index > -1) {
        this.selectId.splice(index, 1);
      } else {
        this.selectId.push(val.id);
      }
    },
    // 搜索
    onSearch(val) {
      this.allSetList.forEach((item) => {
        if (item.name.includes(val)) {
          item.isShow = true;
        } else {
          item.isShow = false;
        }
      });
    },
    // 判断两个数组是否相同
    isSame(source, target) {
      const isArray = Array.isArray(source) && Array.isArray(target);
      if (isArray) {
        if (source.length !== target.length) {
          return false;
        }
        return !source.some((value, index) => value !== target[index]);
      }
      return source === target;
    },
  },
};
</script>

<style lang="postcss" scoped>
  .bk-cascade {
    position: relative;
    border: 1px solid #c4c6cc;
    background: #fff;
    border-radius: 2px;
    width: 162px;
    height: 32px;
    line-height: 30px;
    font-size: 12px;
    color: #63656e;
    cursor: pointer;

    &.is-focus {
      border-color: #3a84ff;
      box-shadow: 0px 0px 4px rgba(58, 132, 255, .4);

      .bk-cascade-angle {
        transform: rotate(-180deg);
      }
    }

    &:hover {
      .bk-cascade-clear {
        display: block;
      }
    }

    .bk-cascade-angle {
      position: absolute;
      right: 2px;
      top: 4px;
      color: #979ba5;
      font-size: 22px;
      transition: transform .3s cubic-bezier(.4, 0, .2, 1);
      pointer-events: none;
    }

    .bk-cascade-clear {
      display: none;
      position: absolute;
      right: 6px;
      top: 8px;
      width: 13px;
      height: 13px;
      background-color: #c4c6cc;
      font-size: 13px;
      color: #fff;
      z-index: 100;

      &:before {
        display: block;
        transform: scale(.7);
      }

      &:hover {
        background-color: #979ba5;
      }
    }

    .bk-cascade-name {
      height: 30px;
      padding: 0 36px 0 11px;
    }

    .placeholder-text {
      font-size: 12px;
      color: #c7d1e3;
    }
  }

  /deep/ .bk-cascade-dropdown-content {
    height: 100%;
    border: 1px solid #c4c6cc;
    box-shadow: 0px 2px 6px 0px rgba(0,0,0,.1);
    border-radius: 2px;
    line-height: 32px;
    background: #fff;
    color: #c4c6cc;
    overflow: hidden;
  }

  .bk-cascade-panel {
    height: 100%;
    border-right: 1px solid #dcdee5;
    display: flex;

    .bk-cascade-panel-ul {
      height: 100%;
      width: 109px;

      .bk-option {
        padding-left: 11px;
        position: relative;
        cursor: pointer;

        .bk-icon {
          position: absolute;
          top: 7px;
          right: 2px;
          font-size: 20px;
        }

        &:hover {
          color: #3a84ff;
          background: #eaf3ff;
        }

        &.is-selected {
          color: #3a84ff;
          background-color: #f4f6fa;
        }
      }
    }
  }

</style>
