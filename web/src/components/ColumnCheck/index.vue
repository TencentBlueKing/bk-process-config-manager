<template>
  <div class="check">
    <bk-button ext-cls="check-btn-loading" size="small" v-if="loading" :loading="loading"></bk-button>
    <template v-else>
      <bk-checkbox
        :value="checkValue"
        :indeterminate="halfCheck"
        :disabled="!disabled"
        :class="{
          'all-check': checkType.active === 'all'
        }"
        @change="handleCheckChange">
      </bk-checkbox>
      <!-- <bk-popover
          ref="popover"
          theme="light agent-operate"
          trigger="click"
          placement="bottom"
          :arrow="false"
          offset="26, 0"
          :on-show="handleOnShow"
          :on-hide="handleOnHide">
          <div class="icon-container">
            <i class="bk-icon icon-angle-down" :class="isDropDownShow && 'active'"></i>
          </div>
          <template slot="content">
            <ul class="dropdown-list">
              <template v-for="(item, index) in checkType.list">
                <li class="list-item" :key="index" @click="handleCheckAll(item.id)">
                  {{ item.name }}
                </li>
              </template>
            </ul>
          </template>
      </bk-popover> -->
    </template>
  </div>
</template>
<script>
export default {
  name: 'ColumnCheck',
  props: {
    // 是否半选
    indeterminate: {
      type: Boolean,
      default: false,
    },
    // 是否全选
    isAllChecked: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      checkValue: false,
      checkType: {
        active: 'current',
        list: [
          {
            id: 'current',
            name: this.$t('本页全选'),
          },
          {
            id: 'all',
            name: this.$t('跨页全选'),
          },
        ],
      },
      isDropDownShow: false,
    };
  },
  computed: {
    halfCheck() {
      return this.indeterminate && !this.isAllChecked;
    },
  },
  watch: {
    isAllChecked(v) {
      this.checkValue = v;
    },
  },
  methods: {
    /**
             * 全选操作
             * @param {String} type 全选类型：1. 本页权限 2. 跨页全选
             */
    handleCheckAll(type) {
      this.checkType.active = type;
      this.$emit('change', true, type);
      this.$refs.popover && this.$refs.popover.instance.hide();
    },
    /**
             * 勾选事件
             */
    handleCheckChange(value) {
      this.checkValue = value;
      this.$emit('change', this.checkValue);
    },
    handleOnShow() {
      this.isDropDownShow = true;
    },
    handleOnHide() {
      this.isDropDownShow = false;
    },
  },
};
</script>
<style lang="postcss" scoped>
  .check {
    .all-check {
      >>> .bk-checkbox {
        background-color: #fff;

        &::after {
          border-color: #3a84ff;
        }
      }
    }

    .indeterminate {
      >>> .bk-checkbox {
        &::after {
          background: #3a84ff;
        }
      }
    }

    .icon-container {
      display: flex;
      justify-content: center;
      align-items: center;
      position: relative;
      top: 3px;
    }

    .icon-angle-down {
      font-size: 22px;
      cursor: pointer;
      color: #63656e;
      transform: rotate(0deg);
      transition: transform .3s cubic-bezier(.4, 0, .2, 1);

      &:hover {
        color: #0094ff;
      }

      &.active {
        transform: rotate(-180deg);
      }
    }

    .check-btn-loading {
      padding: 0;
      min-width: auto;
      border: 0;
      text-align: left;
      background: transparent;

      >>> .bk-button-loading {
        position: static;
        transform: translateX(0);

        .bounce4 {
          display: none;
        }
      }
    }
  }

  .dropdown-list {
    padding: 6px 0;
    background-color: #fff;

    .list-item {
      padding: 0 16px;
      line-height: 32px;
      font-size: 12px;
      color: #63656e;
      cursor: pointer;

      &:hover {
        color: #3a84ff;
        background: #eaf3ff;
      }
    }
  }
</style>
