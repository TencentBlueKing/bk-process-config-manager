<template>
  <div class="process-attribute-container">
    <!-- :header-cell-class-name="getellClassName" -->
    <bk-table
      ref="table"
      v-bkloading="{ isLoading: loading, zIndex: 0 }"
      :class="['expand-table', { edit, 'right-shadow-table': rightShadow }]"
      v-bind="$attrs"
      v-on="$listeners">
      <template slot="prepend">
        <slot name="prepend"></slot>
      </template>
      <template slot="empty">
        <slot name="empty"></slot>
      </template>
      <!-- 暂定 都为多级表头 -->
      <bk-table-column
        v-for="parent in tableHead"
        :key="parent.key"
        align="center"
        v-bind="{
          ...parent,
          [parent.isExpandable ? 'renderHeader' : 'other']: headRenderExpand
        }">
        <!-- 默认有子集 -->
        <bk-table-column
          v-if="parent.isExpandable && !parent.isExpand"
          align="center"
          v-bind="{
            ...parent,
            prop: parent.key
          }"
          :render-header="headRenderStatus">
          <template slot-scope="{ row }">
            <img class="status-img" :src="getGroupStatus(row, parent.child)">
          </template>
        </bk-table-column>
        <template v-else>
          <template v-for="head in parent.child">
            <!-- Column - 跨页全选 -->
            <template v-if="head.type === 'selection'">
              <bk-table-column v-if="openCheckAll" :key="head.prop" :render-header="checkRender">
                <div slot-scope="{ row }" @click.stop>
                  <bk-checkbox
                    :value="row.rowSelect"
                    :disabled="row.disabled"
                    @change="handleRowCheck(row)">
                  </bk-checkbox>
                </div>
              </bk-table-column>
              <bk-table-column v-else :key="head.prop" v-bind="head"></bk-table-column>
            </template>
            <!-- Column - 自定义slot, slotNameStr -->
            <bk-table-column
              v-else-if="head.slotNameStr"
              :key="head.prop"
              v-bind="head">
              <template slot-scope="{ row, $index }">
                <slot :name="head.slotNameStr" :row="row" :$index="$index"></slot>
              </template>
            </bk-table-column>
            <bk-table-column class-name="edit-cell" v-else-if="edit && head.editAble" :key="head.prop" v-bind="head">
              <template slot-scope="{ row, $index }">
                <div
                  class="bk-form-control edit-input"
                  v-if="head.prop === editProp && editIndex === $index">
                  <div class="bk-input-text">
                    <input
                      ref="editInput"
                      class="bk-form-input pr10"
                      type="text"
                      v-model.trim="editValue"
                      :placeholder="$t('请输入')"
                      @blur.capture="handleEditBlur(...arguments, row[head.prop], head)"
                      @keyup.enter.native="handleEditEnter">
                  </div>
                </div>
                <div
                  v-else
                  v-bk-overflow-tips
                  :class="['text-content', { 'disabled': row.disabled }]"
                  @click="handleEditfocus(head.prop, row, $index)">
                  <bk-popover :disabled="!row.disabled" placement="top" theme="light">
                    <span v-if="!isEmpty(row[head.prop])">{{ row[head.prop] }}</span>
                    <div v-else style="display: block; width: 100%; height: 100%;"></div>
                    <i18n path="跳转服务模板" slot="content">
                      <span class="text-cursor primary" @click="handleGoServeTemp(row)">{{ $t('服务模版') }}</span>
                    </i18n>
                  </bk-popover>
                </div>
                <!-- <div
                  :class="['text-content', { 'disabled': row.disabled }]"
                  v-else
                  @click="handleEditfocus(head.prop, row, $index)">
                  <span>{{ emptyCell(row[head.prop]) }}</span>
                </div> -->
              </template>
            </bk-table-column>
            <!-- Column - 常规 -->
            <bk-table-column v-else :key="head.prop" v-bind="head">
              <template slot-scope="{ row }">
                {{ emptyCell(row[head.prop]) }}
              </template>
            </bk-table-column>
          </template>
        </template>
      </bk-table-column>
      <bk-table-column v-if="rightShadow" fixed="right" :width="1">
        <bk-table-column fixed="right" :width="1" />
      </bk-table-column>

      <TableException
        slot="empty"
        :delay="loading"
        :type="emptyType"
        @empty-clear="emptySearchClear" />
    </bk-table>
  </div>
</template>

<script>
import ExpandTh from './expand-th';
import Correct from '@/assets/images/icon-correct.svg';
import Unfinished from '@/assets/images/icon-unfinished.svg';

export default {
  name: 'ExpandTable',
  props: {
    loading: {
      type: Boolean,
      default: false,
    },
    tableHead: {
      type: Array,
      default: () => ([]),
    },
    // 跨页全选 - 与全选做区分
    checkAll: {
      type: Boolean,
      default: false,
    },
    checkRender: {
      type: Function,
      default: null,
    },
    edit: {
      type: Boolean,
      default: true,
    },
    editRules: {
      type: Object,
      default: () => ({}),
    },
    // 未完成加载
    undoneLoading: {
      type: Boolean,
      default: false,
    },
    rightShadow: {
      type: Boolean,
      default: true,
    },
    emptyText: {
      type: String,
      default: '',
    },
    emptyType: {
      type: String,
      default: 'empty',
    },
  },
  data() {
    return {
      editProp: '',
      editIndex: null,
      editValue: '',
    };
  },
  computed: {
    openCheckAll() {
      return this.checkAll && !!this.checkRender;
    },
  },
  methods: {
    /*
      * 根据实际需求，不做过多的配置化
      * 1、一级表头自定义渲染（headRenderExpand）* & 收起时的 二级表头自定义渲染（headRenderStatus） & 收起时的 td 自定义渲染（getGroupStatus） 函数未抛出。
      * 2、跨页全选 渲染函数 抛出
      * 3、单页全选之类的按常规传参 - 未做过多测试
    */

    handleRowCheck(row) {
      row.rowSelect = !row.rowSelect;
      this.$emit('rowCheck', row);
    },
    headRenderExpand(h, { $index }) {
      const parentHead = this.tableHead[$index];
      return h(ExpandTh, {
        props: {
          column: parentHead,
          isExpand: parentHead.isExpand,
        },
        on: {
          'click-expand': (isExpand) => {
            parentHead.isExpand = isExpand;
          },
        },
      });
    },
    // 二级表头折叠是显示的内容
    headRenderStatus(h, { column }) {
      // 加载未完成数量 - 带确认的优化
      if (this.undoneLoading) {
        return h('bk-button', {
          props: {
            icon: 'loading',
            text: true,
            disabled: true,
          },
        });
      }
      const parentHead = this.tableHead.find(parent => parent.key === column.property);
      if (parentHead && parentHead.hasUndone) {
        return h('img', {
          class: 'status-img',
          style: { cursor: 'pointer' },
          attrs: { src: Unfinished },
          on: {
            click: () => this.handSubHeadClick({ column, parent: parentHead }),
          },
        });
      }
      return h('img', {
        class: 'status-img',
        attrs: { src: Correct },
      });
    },
    // 二级表头点击事件
    handSubHeadClick({ column, parent }) {
      this.$emit('sub-head-click', { column, parent });
    },
    handleEditfocus(prop, row, index) {
      if (!row.disabled && !this.editProp) {
        this.editProp = prop;
        this.editIndex = index;
        this.editValue = row[prop];
        this.$nextTick(() => {
          this.$refs.editInput[0] && this.$refs.editInput[0].focus();
        });
      }
    },
    handleEditBlur(event, cellValue, head) {
      let hasError = false;
      let errorMsg = '';
      const ruleList = this.editRules[this.editProp];
      const editStr = `${this.editValue}`;
      const cellStr = `${cellValue}`;
      // 建立在与原始值不相等的情况下
      if (editStr !== cellStr && ruleList) {
        // 值为空时
        if (!editStr) {
          // const rule = ruleList.find(item => !!item.required)
          // if (rule) {
          //     hasError = true
          //     errorMsg = rule.message
          // }
          this.editProp = '';
          this.editIndex = null;
          return;
        }
        ruleList.forEach((rule) => {
          hasError = rule.validator ? rule.validator(editStr) : false;
          errorMsg = hasError ? rule.message : '';
        });
      }
      if (hasError) {
        this.$bkMessage({
          message: errorMsg,
          theme: 'error',
        });
        if (event && event.preventDefault) {
          event.preventDefault();
        }
        this.$refs.editInput[0] && this.$refs.editInput[0].focus();
        return false;
      }
      if (editStr !== cellStr) {
        this.$emit('cell-edit', {
          prop: this.editProp,
          value: head.type === 'number' ? parseInt(this.editValue) : this.editValue,
          row: this.$attrs.data[this.editIndex],
          index: this.editIndex,
        });
      }
      this.editProp = '';
      this.editIndex = null;
    },
    handleEditEnter() {
      this.$refs.editInput[0] && this.$refs.editInput[0].blur();
    },
    handleGoServeTemp(row) {
      this.$emit('eidt-disabled', row);
    },
    // 收起时候 td 展示的内容
    getGroupStatus(row, child) {
      return child && child.some(key => !row[key.prop] && row[key.prop] !== 0) ? Unfinished : Correct;
    },
    isEmpty(val) {
      return val === null || val === undefined || val === '';
    },
    emptyCell(content) {
      return !this.isEmpty(content) ? content : this.emptyText;
    },
    clearSelection() {
      this.$refs.table.clearSelection();
    },
  },
};
</script>

<style lang="postcss" scoped>
  .text-cursor {
    cursor: pointer;
  }

  .primary {
    color: #3a84ff;
  }

  .expand-table {
    width: 100%;
  }

  >>> .bk-table {
    th.is-hidden > .cell,
    td.is-hidden > .cell {
      opacity: 1;
    }

    th.bk-table-column-selection .cell,
    td.bk-table-column-selection .cell {
      padding: 0;
    }

    &.edit-table {
      tr.bk-table-row.hover-row >td {
        background-color: transparent;
      }

      td.edit-cell {
        .cell {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          padding-left: 0;
          padding-right: 0;
        }

        .text-content {
          height: 42px;
          line-height: 42px;
          padding: 0 16px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          cursor: text;

          &:not(.disabled) {
            .bk-tooltip,
            .bk-tooltip-ref {
              display: inline;
            }

            &:hover {
              background: #f0f1f5;
            }
          }

          &.disabled {
            padding: 0;
            cursor: not-allowed;

            .bk-tooltip-ref {
              padding: 0 16px;
            }
          }
        }

        .edit-input .bk-form-input {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          height: 41px;
          padding: 0 16px;
        }

        .bk-tooltip,
        .bk-tooltip-ref {
          min-width: 100%;
          height: 100%;
        }
      }
    }

    &.right-shadow-table {
      .bk-table-fixed-right {
        box-shadow: 0 0 10px #323232;
      }

      .is-scrolling-right ~ .bk-table-fixed-right {
        box-shadow: none;
      }
    }

    .disabled-row {
      color: #979ba5;
    }

    .show-tag-column .cell {
      position: relative;
      padding-left: 60px;
    }

    .expand-th {
      overflow: visible;
      z-index: 2;

      .cell,
      .bk-table-header-label {
        overflow: visible;
      }
    }

    .undone {
      color: #ff9c01;
    }

    .status-img {
      width: 18px;
      height: 18px;
      vertical-align: text-bottom;
    }

    .status-icon {
      height: 18px;
      border-radius: 9px;

      &.status-box {
        display: flex;
        justify-content: center;

        /* cursor: pointer; */
      }

      &.num {
        padding: 0 6px;
        line-height: 16px;
        border: 1px solid #ffb848;
      }

      &.undone {
        background: #ffedd1;
      }
    }
  }
</style>
