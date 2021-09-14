<template>
  <div>
    <ExpandTable
      :table-head="tableHead"
      :data="tableData"
      :pagination="pagination"
      check-all
      :check-render="renderSelectionHeader"
      :row-class-name="setRowClassName"
      @rowCheck="handleRowCheck"
      @page-change="handlePageChange"
      @sub-head-click="handSubHeadClick">
      <div class="selection-tips" slot="prepend">
        <div>{{ $t('已选') }}<span class="tips-num">{{ selectionCount }}</span>{{ $t('条') }},</div>
        <bk-button ext-cls="tips-btn" text>
          {{ $t('选择所有') }}<span class="tips-num">{{ pagination.count }}</span>{{ $t('条') }}
        </bk-button>
        <bk-button ext-cls="tips-btn" text>{{ $t('取消选择所有数据') }}</bk-button>
      </div>
      <!-- 进程类型 -->
      <template slot="isTemplate" slot-scope="{ row }">
        <span :class="['table-tag', { 'is-template': row.isTemplate }]">
          {{ row.isTemplate ? $t('模版') : $t('实例') }}
        </span>
      </template>
      <!-- 别名 -->
      <template slot="alias" slot-scope="{ row }">
        <div v-if="row.isTemplate" @click="handleGoServeTemp(row)" class="alias-content">
          <bk-button text>{{ row.alias }}</bk-button>
          <i class="gsekit-icon gsekit-icon-jump-fill primary ml10"></i>
        </div>
        <span v-else>{{ row.alias }}</span>
      </template>
      <!-- 进程启动参数 -->
      <template slot="startParams" slot-scope="{ row }">
        <bk-popover v-if="row.isTemplate" placement="top" theme="light">
          <span disabled style="white-space: nowrap;">{{ row.startParams || '--' }}</span>
          <i18n path="跳转服务模板" slot="content">
            <span class="text-cursor primary" @click="handleGoServeTemp(row)">{{ $t('服务模版') }}</span>
          </i18n>
        </bk-popover>
        <span v-else>{{ row.startParams || '--' }}</span>
      </template>
      <template slot="topo" slot-scope="{ row, $index }">
        {{ `${$index}slot-test: ${row.topo}` }}
      </template>
    </ExpandTable>
  </div>
</template>

<script>
import ExpandTable from '@/components/expand-table/expand-table';
import ColumnCheck from '@/components/ColumnCheck';

export default {
  name: 'ProcessAttribute',
  components: {
    ExpandTable,
  },
  data() {
    return {
      tableHead: [
        {
          label: '',
          props: 'base',
          key: '',
          fixed: true,
          width: 240, // 组件宽度计算不准确，人肉计算已固定fixed宽度总和
          isExpandable: false, // 是否可展开
          isExpand: true, // 是否展开
          isUndoneNum: false, // 未完成数量 - 待定方案
          hasChild: true,
          headerAlign: 'center',
          // 包含子表头
          child: [
            {
              prop: 'selection',
              type: 'selection',
              width: 60,
              // selectable: this.selectableFn,
              // reserveSelection: true,
              fixed: true,
            },
            {
              prop: 'isTemplate',
              width: 70,
              align: 'center',
              slotNameStr: 'isTemplate',
              fixed: true,
            },
            {
              label: '进程别名',
              prop: 'alias',
              width: 120,
              slotNameStr: 'alias',
              fixed: true,
            },
          ],
        },
        {
          label: '进程基本属性',
          props: 'base',
          key: 'attributeBase',
          isExpandable: false,
          isExpand: true,
          isUndoneNum: 333,
          hasChild: true,
          headerAlign: 'center',
          child: [
            {
              label: '进程名称',
              prop: 'name',
              fixed: false,
              tips: '嘿嘿嘿嘿',
            },
            {
              label: '所属拓扑',
              prop: 'topo',
              fixed: false,
              slotNameStr: 'topo',
              showOverflowTooltip: true,
            },
            {
              label: '进程启动参数',
              prop: 'startParams',
              width: 200,
              fixed: false,
              slotNameStr: 'startParams',
              // showOverflowTooltip: true,
              renderHeader: this.tipsRenderHeader,
            },
            {
              label: '进程备注',
              prop: 'remarks',
              fixed: false,
              renderHeader: this.tipsRenderHeader,
            },
          ],
        },
        {
          label: '基础控制配置',
          props: '',
          key: 'controlBase',
          isExpandable: true,
          isExpand: true,
          fixed: false,
          isUndoneNum: 333,
          hasChild: true,
          tips: '哈哈哈',
          child: [
            {
              label: '控制配置1',
              prop: 'control1',
              fixed: false,
            },
            {
              label: '控制配置2',
              prop: 'control2',
              fixed: false,
            },
            {
              label: '控制配置3',
              prop: 'control3',
              fixed: false,
            },
            {
              label: '控制配置4',
              prop: 'control4',
              fixed: false,
            },
          ],
        },
        {
          label: '启动配置',
          props: '',
          key: 'startBase',
          width: 'auto',
          isExpandable: true,
          isExpand: true,
          fixed: false,
          isUndoneNum: 1231,
          hasChild: true,
          child: [
            {
              label: '启动配置1',
              prop: 'start1',
              fixed: false,
            },
            {
              label: '启动配置2',
              prop: 'start2',
              fixed: false,
            },
            {
              label: '启动配置3',
              prop: 'start3',
              fixed: false,
            },
            {
              label: '启动配置4',
              prop: 'start4',
              fixed: false,
            },
          ],
        },
        {
          label: '停止配置',
          props: '',
          key: 'stopBase',
          width: 'auto',
          isExpandable: true,
          isExpand: true,
          fixed: false,
          isUndoneNum: 0,
          hasChild: true,
          child: [
            {
              label: '停止配置1',
              prop: 'stop1',
              fixed: false,
            },
            {
              label: '停止配置2',
              prop: 'stop2',
              fixed: false,
            },
            {
              label: '停止配置3',
              prop: 'stop3',
              fixed: false,
            },
          ],
        },
        {
          label: '停止配置',
          props: '',
          key: 'stopBase1',
          width: 'auto',
          isExpandable: true,
          isExpand: true,
          fixed: false,
          isUndoneNum: 0,
          hasChild: true,
          child: [
            {
              label: '停止配置1',
              prop: 'stop1',
              fixed: false,
            },
            {
              label: '停止配置2',
              prop: 'stop2',
              fixed: false,
            },
            {
              label: '停止配置3',
              prop: 'stop3',
              fixed: false,
            },
          ],
        },
        {
          label: '停止配置',
          props: '',
          key: 'stopBase2',
          width: 'auto',
          isExpandable: true,
          isExpand: true,
          fixed: false,
          isUndoneNum: 0,
          hasChild: true,
          child: [
            {
              label: '停止配置1',
              prop: 'stop1',
              fixed: false,
            },
            {
              label: '停止配置2',
              prop: 'stop2',
              fixed: false,
            },
            {
              label: '停止配置3',
              prop: 'stop3',
              fixed: false,
            },
          ],
        },
      ],
      tableData: [
        { id: 1, disabled: true, isTemplate: true, alias: 'nginx', name: 'nginx', topo: '广东大区三 / centerdb / 共 20 个实例', startParams: '-c /data/nginx/conf/game.cfg', remarks: '登陆模块', control1: 'control1', control2: 'control2', control3: 'control3', control4: '', start1: 'start1', start2: 'start2', start3: 'start3', start4: 'start4', stop1: 'stop1', stop2: 'stop2', stop3: 'stop3' },
        { id: 2, disabled: true, isTemplate: true, alias: 'nginx', name: 'nginx', topo: '广东大区三 / centerdb / 共 20 个实例', startParams: '-c /data/nginx/conf/game.cfg', remarks: '登陆模块', control1: 'control1', control2: 'control2', control3: 'control3', control4: 'control4', start1: 'start1', start2: 'start2', start3: 'start3', start4: 'start4', stop1: 'stop1', stop2: 'stop2', stop3: 'stop3' },
        { id: 3, alias: 'nginx', name: 'nginx', topo: '广东大区三 / centerdb / 共 20 个实例', startParams: '-c /data/nginx/conf/game.cfg', remarks: '登陆模块', control1: 'control1', control2: '', control3: 'control3', control4: 'control4', start1: 'start1', start2: 'start2', start3: 'start3', start4: 'start4', stop1: 'stop1', stop2: 'stop2', stop3: 'stop3' },
        { id: 4, alias: 'nginx', name: 'nginx', topo: '广东大区三 / centerdb / 共 20 个实例', startParams: '-c /data/nginx/conf/game.cfg', remarks: '登陆模块', control1: 'control1', control2: 'control2', control3: 'control3', control4: 'control4', start1: 'start1', start2: 'start2', start3: 'start3', start4: 'start4', stop1: 'stop1', stop2: 'stop2', stop3: 'stop3' },
        { id: 5, alias: 'nginx', name: 'nginx', topo: '广东大区三 / centerdb / 共 20 个实例', startParams: '-c /data/nginx/conf/game.cfg', remarks: '登陆模块', control1: 'control1', control2: 'control2', control3: 'control3', control4: 'control4', start1: 'start1', start2: 'start2', start3: '', start4: 'start4', stop1: 'stop1', stop2: 'stop2', stop3: 'stop3' },
        { id: 6, alias: 'nginx', name: 'nginx', topo: '广东大区三 / centerdb / 共 20 个实例', startParams: '-c /data/nginx/conf/game.cfg', remarks: '登陆模块', control1: 'control1', control2: 'control2', control3: 'control3', control4: 'control4', start1: 'start1', start2: 'start2', start3: 'start3', start4: '', stop1: 'stop1', stop2: 'stop2', stop3: 'stop3' },
        { id: 7, alias: 'nginx', name: 'nginx', topo: '广东大区三 / centerdb / 共 20 个实例', startParams: '-c /data/nginx/conf/game.cfg', remarks: '登陆模块', control1: 'control1', control2: 'control2', control3: 'control3', control4: 'control4', start1: 'start1', start2: 'start2', start3: 'start3', start4: 'start4', stop1: 'stop1', stop2: '', stop3: 'stop3' },
        { id: 8, alias: 'nginx', name: 'nginx', topo: '广东大区三 / centerdb / 共 20 个实例', startParams: '-c /data/nginx/conf/game.cfg', remarks: '登陆模块', control1: 'control1', control2: 'control2', control3: 'control3', control4: 'control4', start1: 'start1', start2: 'start2', start3: 'start3', start4: 'start4', stop1: 'stop1', stop2: 'stop2', stop3: 'stop3' },
        { id: 9, alias: 'nginx', name: 'nginx', topo: '广东大区三 / centerdb / 共 20 个实例', startParams: '-c /data/nginx/conf/game.cfg', remarks: '登陆模块', control1: 'control1', control2: 'control2', control3: 'control3', control4: 'control4', start1: 'start1', start2: 'start2', start3: 'start3', start4: 'start4', stop1: 'stop1', stop2: 'stop2', stop3: 'stop3' },
        { id: 23, alias: 'nginx', name: 'nginx', topo: '广东大区三 / centerdb / 共 20 个实例', startParams: '-c /data/nginx/conf/game.cfg', remarks: '登陆模块', control1: 'control1', control2: 'control2', control3: 'control3', control4: 'control4', start1: 'start1', start2: 'start2', start3: 'start3', start4: 'start4', stop1: 'stop1', stop2: 'stop2', stop3: 'stop3' },
      ],
      pagination: {
        current: 1,
        count: 500,
        limit: 10,
      },
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
  mounted() {
    console.log(this.$attrs);
  },
  methods: {
    handlePageChange(page) {
      console.log(page);
      this.pagination.current = page;
    },
    handleFiltersChange() {
      this.$emit('change-filters', this.staticIncomplete);
    },
    handSubHeadClick(data) {
      console.log(data);
    },
    handleGoServeTemp(row) {
      console.log(row);
    },
    renderSelectionHeader() {
      return <ColumnCheck
        ref="customSelectionHeader"
        indeterminate={this.indeterminate}
        isAllChecked={this.isAllChecked}
        loading={this.checkLoading}
        disabled={Boolean(this.tableData.length)}
        onChange={(value, type) => this.handleCheckAll(value, type)}>
      </ColumnCheck>;
    },
    async handleCheckAll(value, type) {
      console.log(value, type);
    },
    setRowClassName({ row }) {
      return row.disabled ? 'disabled-row' : '';
    },
    tipsRenderHeader(h, { column }) {
      return <span class="text-has-tips" v-bk-tooltips={ this.subHeadMap[column.property] }>{ column.label }</span>;
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

  >>> .disabled-row {
    color: #979ba5;
  }

  .table-tag {
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
