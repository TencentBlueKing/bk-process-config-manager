<template>
  <section>
    <div class="table-statistics">
      <i18n v-if="isBizProcess" class="static-total" path="进程总数"><span class="primary">{{ staticTotal }}</span></i18n>
      <i18n v-else class="static-total" path="模板进程总数"><span class="primary">{{ staticTotal }}</span></i18n>
      <span class="static-incomplete" v-if="staticIncomplete">
        {{ $t('配置缺失') }}:
        <span class="text-cursor undone" v-bk-tooltips="$t('筛选')" @click.stop="handleFiltersChange">
          {{ staticIncomplete }}
        </span>
      </span>
    </div>
    <!-- :check-render="renderSelectionHeader" -->
    <ExpandTable
      ref="expandTable"
      check-all
      row-key="id"
      ext-cls="edit-table"
      :table-head="tableHead"
      :loading="loading"
      :data="tableData"
      :edit-rules="editRules"
      :pagination="pagination"
      :row-class-name="setRowClassName"
      :cell-class-name="setCellClassName"
      :header-cell-class-name="getellClassName"
      :empty-type="emptyType"
      @rowCheck="handleRowCheck"
      @cell-edit="handleCellEdit"
      @eidt-disabled="handleEidtDisabled"
      @page-change="handlePageChange"
      @sub-head-click="handFilterUndone"
      @page-limit-change="handlePageLimitChange"
      @selection-change="handleSelectionChange"
      @empty-clear="emptySearchClear">
      <!-- <div class="selection-tips" v-if="selections.length" slot="prepend">
        <div>
          {{ $t('已选') }}
          <span class="tips-num">{{ selections.length }}</span>
          {{ $t('条') }},
        </div>
        <bk-button ext-cls="tips-btn" text @click="handleCancelSelect">{{ $t('取消选择所有数据') }}</bk-button>
      </div> -->
      <EmptyServiceBox
        slot="empty"
        v-if="!tableData.length && !isSearch"
        :title="$t('暂无进程')"
        :desc="isBizProcess ? $t('当前业务拓扑下暂无进程') : $t('当前服务模板下暂无进程')"
        :desc-slot="'创建进程slot'"
        @click-link="handleEmptyLink"
      />
      <!-- 进程类型 -->
      <template slot="isTemplate" slot-scope="{ row }">
        <span :class="['table-tag', { 'is-template': row.isTemplate }]">
          {{ row.isTemplate ? $t('模版') : $t('实例') }}
        </span>
      </template>
      <!-- 别名 -->
      <template slot="alias" slot-scope="{ row }">
        <span v-if="row.showTypeTag" :class="['table-tag', { 'is-template': row.isTemplate }]">
          {{ row.isTemplate ? $t('模版') : $t('实例') }}
        </span>
        <div v-if="row.isTemplate" @click="handleEidtDisabled(row)" class="text-cursor">
          <bk-button text>{{ row.bk_process_name }}</bk-button>
          <i class="gsekit-icon gsekit-icon-jump-fill primary ml10"></i>
        </div>
        <span v-else>{{ row.bk_process_name }}</span>
      </template>
      <!-- 进程启动参数 -->
      <!-- <template slot="startParams" slot-scope="{ row }">
        <bk-popover v-if="row.isTemplate" placement="top" theme="light">
          <span disabled style="white-space: nowrap;">{{ row['bk_start_param_regex'] }}</span>
          <span slot="content">
            模版进程信息，请前往 <span class="text-cursor primary"> 服务模版 </span>编辑
          </span>
        </bk-popover>
        <span v-else>{{ row['bk_start_param_regex'] || '--' }}</span>
      </template> -->
      <template slot="topo" slot-scope="{ row }">
        {{ row.topoPath }}
      </template>
    </ExpandTable>
  </section>
</template>

<script>
/**
 * example-expand-table 可共参考
 */
import ExpandTable from '@/components/expand-table/expand-table';
import EmptyServiceBox from '@/components/Empty/EmptyServiceBox';

export default {
  name: 'ProcessTable',
  components: {
    ExpandTable,
    EmptyServiceBox,
  },
  props: {
    loading: {
      type: Boolean,
      default: false,
    },
    isBizProcess: {
      type: Boolean,
      default: true,
    },
    selectedNode: {
      type: Object,
      default: () => ({}),
    },
    tableData: {
      type: Array,
      default: () => [],
    },
    tableHead: {
      type: Array,
      default: () => [],
    },
    staticTotal: {
      type: Number,
      default: 0,
    },
    staticIncomplete: {
      type: Number,
      default: 0,
    },
    selections: {
      type: Array,
      default: () => [],
    },
    pagination: {
      type: Object,
      default: () => ({
        current: 1,
        count: 0,
        limit: 10,
      }),
    },
    editRules: {
      type: Object,
      default: () => ({}),
    },
    isSearch: {
      type: Boolean,
      default: false,
    },
    emptyType: {
      type: String,
      default: 'empty',
    },
  },
  data() {
    return {
      testExpand: true,
      indeterminate: false,
      isAllChecked: false,
      checkLoading: false,
    };
  },
  computed: {
    openCheckAll() {
      return this.checkAll && !!this.checkRender;
    },
  },
  methods: {
    handleRowCheck(row) {
      console.log(row);
    },
    handlePageChange(page, limit) {
      this.$emit('page-change', { page, limit: limit || this.pagination.limit });
    },
    handlePageLimitChange(limit) {
      this.handlePageChange(1, limit);
    },
    handleFiltersChange() {
      this.$emit('change-filters', this.staticIncomplete);
    },
    handleSelectionChange(selection) {
      this.$emit('selection-change', selection);
    },
    // 需要把这个fn做成参数传递过去
    handleCellEdit(data) {
      this.$emit('cell-edit', data);
    },
    handFilterUndone(data) {
      this.$emit('sub-head-filter', data);
    },
    handleEidtDisabled(row) {
      this.$emit('eidt-disabled', row);
    },
    handleCancelSelect() {
      this.$refs.expandTable.clearSelection();
    },
    selectableFn(row) {
      return !row.disabled;
    },
    setRowClassName({ row }) {
      return row.disabled ? 'disabled-row' : '';
    },
    // 给可折叠的表头添加 超出不隐藏class expand-th
    getellClassName({ row, rowIndex, columnIndex }) {
      const nameStr = !rowIndex && this.tableHead[columnIndex] && this.tableHead[columnIndex].isExpandable ? 'expand-th' : '';
      return this.isBizProcess && row[columnIndex].property === 'bk_process_name' ? `${nameStr} show-tag-column` : nameStr;
    },
    setCellClassName({ row, column }) {
      return column.property === 'bk_process_name' && row.showTypeTag ? 'show-tag-column' : '';
    },
    // 表格无数据 - 只缺实例或者进程
    handleEmptyLink() {
      let queryStr = `${window.PROJECT_CONFIG.CMDB_URL}/#/business/${this.$store.state.bizId}/`;
      if (this.isBizProcess) {
        const { bk_inst_id: bkIinstId, bk_obj_id: bkObjId, topoType, topoParent } = this.selectedNode;
        if (topoType === 'set' || topoType === 'module' || topoType === 'serviceTemplate') {
          queryStr = `${queryStr}index?node=${bkObjId}-${bkIinstId}&tab=serviceInstance&view=instance`;
        } else if (topoType === 'serviceInstance') {
          queryStr = `${queryStr}index?node=${topoParent.bk_obj_id}-${topoParent.bk_inst_id}&tab=serviceInstance&view=instance`;
        }
      } else {
        // 新增进程
        queryStr += `service/operational/template/${this.selectedNode.id}?tab=config`;
      }
      window.open(queryStr, '_blank');
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

  .undone {
    color: #ff9c01;
  }

  .table-statistics {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding: 0 16px;
    height: 42px;
    background: #f0f1f5;
    border: 1px solid #dcdee5;
    border-radius: 2px;
    font-weight: bold;
    color: #63656e;

    .static-total {
      font-size: 14px;
    }

    .static-incomplete {
      font-size: 13px;
    }
  }

  .selection-tips {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 32px;
    font-size: 12px;
    color: #313238;
    background: #ebecf0;

    .tips-num {
      font-weight: bold;
    }

    .tips-btn {
      font-size: 12px;
      margin-left: 5px;
    }
  }

  >>> .show-tag-column .cell {
    padding-left: 60px;
    line-height: 20px;
  }

  .table-tag {
    position: absolute;
    top: 1px;
    left: 15px;
    display: inline-block;
    width: 32px;
    line-height: 18px;
    border-radius: 2px;
    text-align: center;
    color: #979ba5;
    background: #f0f1f5;

    &.is-template {
      color: #3a84ff;
      background: #e1ecff;
    }
  }
</style>
