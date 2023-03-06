<template>
  <div class="history-list" v-test="'history'">
    <div class="history-list-header">{{ $t('任务历史') }}</div>
    <div class="search-area">
      <bk-search-select
        ref="searchSelect"
        v-test.common="'searchSelect'"
        :data="searchSelectData"
        v-model="searchSelectValue"
        :show-condition="false"
        @show-menu="handleSearchSelectShowMenu"
        @change="handleSearchSelectChange">
      </bk-search-select>
      <bk-date-picker
        v-test="'picker'"
        v-model="initDateTimeRange"
        :placeholder="$t('选择日期时间范围')"
        :type="'datetimerange'"
        @pick-success="onDataPickerPick"
        @clear="handleClearDate">
      </bk-date-picker>
    </div>
    <bk-table
      :max-height="$store.state.pageHeight - 187"
      ext-cls="king-table"
      :data="tableData"
      v-bkloading="{ isLoading }"
      :pagination="pagination"
      :row-class-name="handlerRowClassName"
      @sort-change="handleSortChange"
      @row-click="handleRowClick"
      @page-change="handlePageChange"
      @page-limit-change="handlePageLimitChange">
      <bk-table-column prop="id" :label="$t('ID')" width="90">
        <template slot-scope="props">
          <span class="button-text" v-test="'viewTask'">{{ props.row.id }}</span>
        </template>
      </bk-table-column>
      <bk-table-column
        prop="job_object"
        :label="$t('任务对象')"
        :min-width="columnMinWidth['job_object']"
        :render-header="renderFilterHeader">
        <template slot-scope="props">
          <span>{{ jobObject[props.row.job_object] }}</span>
        </template></bk-table-column>
      <bk-table-column
        prop="job_action"
        :label="$t('动作')"
        :min-width="columnMinWidth['job_action']"
        :render-header="renderFilterHeader">
        <template slot-scope="props">
          <span>{{ jobAction[props.row.job_action] }}</span>
        </template></bk-table-column>
      <bk-table-column prop="job_env" :label="$t('环境类型')" :min-width="columnMinWidth['job_env']">
        <template slot-scope="{ row }">
          <span>{{ setEnv[row.expression_scope.bk_set_env] || '--' }}</span>
        </template></bk-table-column>
      <bk-table-column prop="expression" :label="$t('操作范围')" :min-width="columnMinWidth['expression']">
        <div v-bk-overflow-tips slot-scope="{ row }">
          {{ row.expression }}
        </div>
      </bk-table-column>
      <bk-table-column
        prop="created_by"
        :label="$t('执行账户')"
        show-overflow-tooltip
        :min-width="columnMinWidth['created_by']"
        :render-header="renderFilterHeader" />
      <bk-table-column
        prop="start_time"
        :label="$t('开始时间')"
        sortable="custom"
        :min-width="columnMinWidth['start_time']">
        <template slot-scope="props">
          <div v-bk-overflow-tips>{{ props.row.start_time || '--' }}</div>
        </template>
      </bk-table-column>
      <bk-table-column
        prop="end_time"
        :label="$t('结束时间')"
        sortable="custom"
        :min-width="columnMinWidth['end_time']">
        <template slot-scope="props">
          <div v-bk-overflow-tips>{{ props.row.end_time || '--' }}</div>
        </template>
      </bk-table-column>
      <bk-table-column prop="timeout" :label="$t('执行耗时')"
                       :min-width="columnMinWidth['timeout']">
        <template slot-scope="props">
          <span>{{ props.row.timeout || '--' }}</span>
        </template>
      </bk-table-column>
      <bk-table-column
        prop="status"
        :label="$t('执行状态')"
        :render-header="renderFilterHeader"
        :min-width="columnMinWidth['status']">
        <template slot-scope="{ row }">
          <!-- 执行状态 -->
          <StatusView v-if="row.status === 'succeeded'" type="success" :text="$t('执行成功')" />
          <StatusView v-else-if="row.status === 'failed'" type="failed" :text="$t('执行失败')" />
          <StatusView v-else-if="row.status === 'running'" type="loading" :text="$t('正在执行')" />
          <StatusView v-else type="loading" :text="$t('等待中')" />
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('操作')" :min-width="columnMinWidth['operate']">
        <div slot-scope="props" @click.stop>
          <bk-button
            v-test="'taskRetry'"
            :disabled="props.row.status !== 'failed'"
            theme="primary"
            text
            @click="onRetyr(props.row)">
            {{ $t('重试') }}</bk-button>
        </div>
      </bk-table-column>
      <TableException
        slot="empty"
        :delay="isLoading"
        :type="tableEmptyType"
        @empty-clear="emptySearchClear" />
    </bk-table>
  </div>
</template>

<script>
import { performTime, modifyFormatDate, formatDate } from '@/common/util';
import tableHeaderMixins from '@/components/FilterHeader/table-header-mixins';
import { debounce } from 'lodash';

export default {
  name: 'HistoryList',
  mixins: [tableHeaderMixins],
  props: {
    jobObject: {
      type: Object,
      default() {
        return {};
      },
    },
    jobAction: {
      type: Object,
      default() {
        return {};
      },
    },
    setEnv: {
      type: Object,
      default() {
        return {};
      },
    },
  },
  data() {
    return {
      filterData: [
        {
          name: this.$t('任务对象'),
          id: 'job_object',
          children: [],
          multiable: true,
        },
        {
          name: this.$t('动作'),
          id: 'job_action',
          children: [],
          multiable: true,
        },
        {
          name: this.$t('执行状态'),
          id: 'status',
          children: [],
          multiable: true,
        },
        {
          name: this.$t('执行账户'),
          id: 'created_by',
          children: [],
          multiable: true,
        },
      ],
      initDateTimeRange: ['', ''],
      tableData: [],
      isLoading: false,
      pagination: {
        current: 1,
        count: 500,
        limit: 50,
      },
      ordering: '', // 排序字段
      runningList: [], // 列表正在执行中id
      selectedIdList: [],
      historyListTimer: null,
      getTaskHistoryList: () => {},
      columnList: [
        { id: 'job_object', label: this.$t('任务对象'), sortable: false, filter: true },
        { id: 'job_action', label: this.$t('动作'), sortable: false, filter: true },
        { id: 'job_env', label: this.$t('环境类型'), sortable: false, filter: false },
        { id: 'expression', label: this.$t('操作范围'), sortable: false, filter: false },
        { id: 'created_by', label: this.$t('执行账户'), sortable: false, filter: true },
        { id: 'start_time', label: this.$t('开始时间'), sortable: true, filter: false },
        { id: 'end_time', label: this.$t('结束时间'), sortable: true, filter: false },
        { id: 'timeout', label: this.$t('执行耗时'), sortable: false, filter: false },
        { id: 'status', label: this.$t('执行状态'), sortable: false, filter: true },
        { id: 'operate', label: this.$t('操作'), sortable: false, filter: false },
      ],
      columnMinWidth: {},
    };
  },
  computed: {
    tableEmptyType() {
      return (this.initDateTimeRange.some(date => !!date) || this.searchSelectValue.length)
        ? 'search-empty'
        : 'empty';
    },
  },
  beforeDestroy() {
    clearTimeout(this.historyListTimer);
  },
  created() {
    this.computedColumnWidth();
    this.getTaskHistoryList = debounce(this.getTaskHistoryListSource, 300);
    const highlightIds = sessionStorage.getItem('taskHistoryHighlightIds');
    if (highlightIds) {
      this.selectedIdList = highlightIds.split(',').map(item => Number(item));
      sessionStorage.removeItem('taskHistoryHighlightIds');
    }
    this.getTaskHistoryList();
    this.getHistoryFilterList();
  },
  methods: {
    // 获取配置文件列表
    async getTaskHistoryListSource() {
      try {
        this.isLoading = true;
        const query = this.getSearchParams();
        const res = await this.$store.dispatch('job/ajaxGetJobList', {
          page: this.pagination.current,
          pagesize: this.pagination.limit,
          ordering: this.ordering,
          query,
        });
        this.pagination.count = res.data.count;
        const runningList = [];
        // 过滤列表添加执行账户条件
        const updatePersonFilters = new Set();
        res.data.list.forEach((item) => {
          updatePersonFilters.add(item.created_by);
          // 处理开始时间
          item.start_time = modifyFormatDate(item.start_time);
          // 处理结束时间
          item.end_time = modifyFormatDate(item.end_time);
          // 计算执行耗时
          item.timeout = performTime(item.start_time, item.end_time);
          // 获取正在执行中的历史id
          if (!['succeeded', 'failed'].includes(item.status)) {
            runningList.push(item.id);
          }
        });
        const perAccount = [...updatePersonFilters].map(item => ({
          name: item,
          id: item,
        }));
        this.tableData = res.data.list;
        this.filterData.forEach((item) => {
          if (item.id === 'created_by') {
            item.children = perAccount;
          }
        });
        if (runningList.length) {
          // 轮询历史列表
          this.runningList = runningList;
          this.setPollHistoryList();
        }
      } catch (error) {
        console.warn(error);
      } finally {
        this.isLoading = false;
      }
    },
    // 轮询历史列表
    setPollHistoryList() {
      try {
        this.historyListTimer && clearTimeout(this.historyListTimer);
        this.historyListTimer = setTimeout(async () => {
          const query = this.getSearchParams();
          const res = await this.$store.dispatch('job/ajaxGetJobList', {
            pagesize: this.pagination.limit,
            query,
          });
          const runningList = [];
          res.data.list.forEach((requestJob) => {
            const jobItem = this.tableData.find(job => job.id === requestJob.id);
            jobItem.status = requestJob.status;
            if (!['succeeded', 'failed'].includes(requestJob.status)) {
              runningList.push(requestJob.id);
            }
          });
          if (runningList.length) {
            // 轮询历史列表
            this.runningList = runningList;
            this.setPollHistoryList();
          }
        }, 5000);
      } catch (error) {
        console.warn(error);
      }
    },
    // 生成搜索参数
    getSearchParams() {
      const params = {};
      const dateTime = this.initDateTimeRange;
      if (dateTime[0]) {
        params.start_time__gte = formatDate(dateTime[0]);
      }
      if (dateTime[1]) {
        params.start_time__lte = formatDate(dateTime[1]);
      }
      if (this.searchSelectValue.length) {
        this.searchSelectValue.forEach((item) => {
          params[item.id] = item.values.map(val => val.id);
        });
      }
      if (this.runningList.length) {
        params.id = this.runningList;
      }
      // 获取时间
      return params;
    },
    // 获取用户列表 任务历史过滤选项
    async getHistoryFilterList() {
      try {
        const filterList = await this.$store.dispatch('meta/ajaxGetHistoryFilterList');
        this.filterData.forEach((item) => {
          const type = `${item.id}_choices`;
          if (!filterList.data[type]) return;
          const chidlren = filterList.data[type].map(val => ({
            name: val.name,
            id: val.id,
          }));
          item.children.push(...chidlren);
        });
        this.searchSelectData = this.filterData;
      } catch (error) {
        console.warn(error);
      }
    },
    handlerRowClassName({ row }) {
      if (this.selectedIdList.includes(row.id)) {
        return 'select-row';
      }
    },
    handleSortChange({ prop, order }) {
      if (order === 'ascending') {
        this.ordering = prop;
      } else if (order === 'descending') {
        this.ordering = `-${prop}`;
      } else {
        this.ordering = '';
      }
      clearTimeout(this.historyListTimer);
      this.runningList = [];
      this.getTaskHistoryList();
    },
    // 整行点击
    handleRowClick(row) {
      this.$emit('getTaskDeatail', row);
      this.$store.commit('routeTaskHistoryDetail', row.id);
    },
    onDataPickerPick() {
      this.getTaskHistoryList();
    },
    handleClearDate() {
      this.initDateTimeRange = ['', ''];
      this.getTaskHistoryList();
    },
    async onRetyr(row) {
      try {
        this.runningList.push(row.id);
        row.status = 'loading';
        await this.$store.dispatch('job/ajaxRetryJob', {
          jobId: row.id,
          data: {
            job_task_id_list: [],
          },
        });
        this.setPollHistoryList();
      } catch (error) {
        console.warn(error);
      }
    },
    handlePageLimitChange(limit) {
      clearTimeout(this.historyListTimer);
      this.runningList = [];
      this.pagination.current = 1;
      this.pagination.limit = limit;
      this.getTaskHistoryList();
    },
    handlePageChange(page) {
      clearTimeout(this.historyListTimer);
      this.runningList = [];
      this.pagination.current = page;
      this.getTaskHistoryList();
    },
    computedColumnWidth() {
      const widthMap = {};
      this.columnList.reduce((obj, item) => {
        obj[item.id] = this.$textTool.getHeadWidth(item.label, item);
        return obj;
      }, widthMap);
      this.columnMinWidth = widthMap;
    },
    emptySearchClear() {
      this.isLoading = true;
      this.handleClearDate();
      this.searchSelectValue = [];
      this.handleSearchSelectChange(this.searchSelectValue);
    },
  },
};
</script>

<style lang="postcss" scoped>
  .history-list {
    height: 100%;
    background: #f5f7fa;
    padding: 18px 60px 24px;

    .history-list-header {
      font-size: 16px;
      color: #313238;
      margin-bottom: 20px;
    }

    .search-area {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;

      /deep/ .bk-search-select {
        width: 500px;
        background-color: #fff;
      }

      /deep/ .bk-date-picker {
        width: 320px;
      }
    }

    /deep/ .king-table {
      background-color: #fff;

      .bk-table-row {
        &:hover {
          cursor: pointer;
        }
      }

      .cell {
        padding-right: 10px;
      }

      .select-row {
        animation: show-select 1.2s;

        @keyframes show-select {
          0% { background: #fff; }

          20% { background: #fff; }

          40% { background: #f0f5ff; }

          60% { background: #fff; }

          80% { background: #f0f5ff; }

          100% { background: #fff; }
        }
      }
    }
  }
</style>
