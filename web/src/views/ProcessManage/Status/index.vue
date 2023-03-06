<template>
  <div class="process-status"
       v-test="'processStatus'" v-bkloading="{ isLoading: checkeStatus === 'loading' && isDataLoading }">
    <EmptyProcess v-if="showEmptyProcess" :completed="checkeStatus === 'completed'"></EmptyProcess>
    <section v-else-if="showNormalProcess">
      <div class="process-status-title">{{ $t('进程管理') }}</div>
      <ButtonGrounp
        :is-selected="Boolean(selectLength)"
        :is-btn-loading="isBtnLoading"
        :job-action="jobAction"
        :is-data-loading="isDataLoading"
        :is-synchronous-loading="isSynchronousLoading"
        :is-allow-issued="isAllowIssued"
        :is-allow-start="isAllowStart"
        :is-allow-stop="isAllowStop"
        :is-selected-all-pages="isSelectedAllPages"
        @operateProcess="operateProcess"
        @operateConfigDistribute="operateConfigDistribute"
        @synchronousProcess="synchronousProcess">
      </ButtonGrounp>
      <!-- 下拉筛选 -->
      <div class="search-content">
        <SelectInstance
          ref="selectInstanceRef"
          :show-button="false"
          @update:isExisted="(value) => isExisted = value"
          @valueChange="valueChange">
        </SelectInstance>
        <div class="search-select-input-container">
          <bk-search-select
            ref="searchSelect"
            v-test.common="'searchSelect'"
            :placeholder="$t('内网IP、云区域')"
            :show-condition="false"
            :data="searchSelectData"
            v-model="searchSelectValue"
            @paste.native.capture.prevent="handlePaste"
            @show-menu="handleSearchSelectShowMenu"
            @change="handleSearchSelectChange">
          </bk-search-select>
        </div>
      </div>

      <!-- 跨页全选提示信息 -->
      <div v-show="isSelectedAllPages" class="selected-all-pages">
        {{ $t('已选') }}
        <span class="count">{{ selectLength }}</span>
        {{ $t('条，跨页全选暂不支持反选，') }}
        <span class="button-text" @click="handleClearSelection">{{ $t('取消') }}</span>
      </div>
      <!-- 表格 -->
      <TableContent
        ref="tableContent"
        v-bkloading="{ isLoading: isDataLoading }"
        :table-data="tableData"
        :pagination="pagination"
        :job-action="jobAction"
        :filter-data="filterData"
        :search-select-data="filterData"
        :search-select-value="searchSelectValue"
        :ordering="ordering"
        :loading="isDataLoading"
        :table-empty-type="tableEmptyType"
        @handleSortChange="handleSortChange"
        @handleFilterHeaderReset="handleFilterHeaderReset"
        @handleFilterHeaderConfirm="handleFilterHeaderConfirm"
        @operateProcess="operateProcess"
        @handleRowCheck="handleRowCheck"
        @selectedAllPages="onSelectedAllPages"
        @handlePageLimitChange="handlePageLimitChange"
        @handlePageChange="handlePageChange"
        @showSideSlider="showSideSlider"
        @empty-clear="handleTableClear">
      </TableContent>
      <!-- 配置下发侧滑面板 -->
      <ConfigDistribute
        v-if="isShow"
        :is-dropdown-mode="isDropdownMode"
        :selected-scope="selectedScope"
        :process-detail="processDetail"
        :title-name="$t('配置下发')"
        @onConfigDistribute="onConfigDistribute"
        @closeSideSlider="closeSideSlider">
      </ConfigDistribute>
      <!-- 操作二次确认弹框 -->
      <bk-dialog
        ext-cls="king-dialog"
        v-model="dialogInfo.visible"
        :render-directive="'if'"
        width="450"
        :mask-close="false"
        @confirm="handleDialogConFirm"
        @cancel="handleDialogCancel"
        :title="dialogInfo.title + $t('进程')">
        <div class="body-prompt">
          {{ $t('确定要') }}
          <span>{{ dialogInfo.title }}</span>
          {{ $t('所选进程？') }}
        </div>
      </bk-dialog>
    </section>
  </div>
</template>

<script>
import TableContent from './TableContent';
import ConfigDistribute from './ConfigDistribute';
import SelectInstance from '@/components/SelectInstance';
import ButtonGrounp from './ButtonGrounp';
import EmptyProcess from '@/components/Empty/EmptyProcess';
import { bus } from '@/common/bus';
import { debounce } from 'lodash';

export default {
  name: 'ProcessStatus',
  components: {
    TableContent,
    ConfigDistribute,
    SelectInstance,
    ButtonGrounp,
    EmptyProcess,
  },
  data() {
    const jobAction = [
      {
        type: 'start',
        actionName: this.$t('启动'),
      }, {
        type: 'stop',
        actionName: this.$t('停止'),
      }, {
        type: 'restart',
        actionName: this.$t('重启'),
      }, {
        type: 'reload',
        actionName: this.$t('重载'),
      }, {
        type: 'force_stop',
        actionName: this.$t('强制停止'),
      }, {
        type: 'set_auto',
        actionName: this.$t('托管'),
      }, {
        type: 'unset_auto',
        actionName: this.$t('取消托管'),
      },
    ];
    return {
      checkeStatus: 'loading', // loading, normal, error, unknow, completed
      localEnv: '', // localStorage 存储的选中环境
      checkedEnv: '', // 当前环境 - 非实时, 仅用于检查; 其它操作取 selectedScope.bk_set_env
      checkedEnvList: [], // 待检查的环境
      hasCheckedAsync: false, // 初始检查是否做个同步操作
      hasCheckedModelList: false, // 是否检查过topo(this.checkStepInstance)
      selectChecks: [],
      isShow: false,
      processDetail: {}, // 进程数据
      isDataLoading: true,
      tableData: [], // 表格数据
      pagination: {
        current: 1,
        count: 0,
        limit: 50,
      },
      selectLength: 0, // 勾选个数
      isSelectedAllPages: false, // 是否为跨页全选
      isDropdownMode: true, // 筛选下拉模式，反之表达式模式
      selectedScope: {
        bk_set_ids: [],
        bk_module_ids: [],
        bk_service_ids: [],
        bk_process_names: [],
        bk_process_ids: [],
        bk_set_env: '',
      },
      processIdList: [], // 选择的进程id
      isBtnLoading: '',
      filterData: [],
      searchSelectValue: [],
      searchSelectData: [],
      // 判断数据列表是否展示
      isMenuShow: false,
      ordering: '', // 排序字段
      isSynchronousLoading: false, // 同步loading
      jobAction,
      dialogInfo: { // 二次确认弹框信息
        visible: false, // 二次确认弹框是否可见
        rowId: null, // 当前点击行的id
        operateType: '', // 操作类型
        title: '', // dialog标题
      },
      prevListLength: 0,
      isMatch: true,
      isExisted: false,
      getTemplateList: () => {},
    };
  },
  computed: {
    showEmptyProcess() {
      return ['error', 'completed'].includes(this.checkeStatus);
    },
    showNormalProcess() {
      return ['unknow', 'normal'].includes(this.checkeStatus);
    },
    // 是否允许下发
    isAllowIssued() {
      const result = this.tableData.some(item => this.processIdList.includes(item.bk_process_id) && item.templateCount);
      return this.isSelectedAllPages ? !this.isSelectedAllPages : !result;
    },
    // 是否允许启动
    isAllowStart() {
      const result = this.tableData.some(item => this.processIdList.includes(item.bk_process_id)
        && item.process_status !== 1);
      return this.isSelectedAllPages ? !this.isSelectedAllPages : !result;
    },
    // 是否允许停止
    isAllowStop() {
      const result = this.tableData.some(item => this.processIdList.includes(item.bk_process_id)
        && item.process_status !== 2);
      return this.isSelectedAllPages ? !this.isSelectedAllPages : !result;
    },
    tableEmptyType() {
      return (this.isExisted || this.searchSelectValue.length) ? 'search-empty' : 'empty';
    },
  },
  watch: {
    showNormalProcess(val) {
      if (val) {
        const { expressionScope } = this.$route.query;
        if (expressionScope) {
          // 需要回填表达式，回填后会触发 valueChange 事件
          this.$nextTick(() => {
            this.$refs.selectInstanceRef.setExpressionValue(JSON.parse(expressionScope));
          });
        } else {
          // 获取实例列表
          if (this.checkedEnv !== '3') {
            this.$nextTick(() => {
              this.$refs.selectInstanceRef.handleSetEnv(this.localEnv || this.checkedEnv);
            });
          }
          this.getTemplateList();
          if (this.showNormalProcess) {
            this.getFilterCondition();
          }
        }
      }
    },
    tableData: {
      handler(val) {
        if (this.isSelectedAllPages) {
          this.selectLength = this.pagination.count;
          return;
        }
        let selectLength = 0;
        val.forEach((item) => {
          if (item.isSelect) {
            selectLength += 1;
          }
        });
        this.selectLength = selectLength;
      },
      deep: true,
    },
    searchSelectValue: {
      handler() {
        if (this.checkeStatus === 'normal' && this.isMatch) {
          this.handleSearchSelectFilter();
          this.handlePageChange(1);
        }
      },
      deep: true,
    },
  },
  created() {
    this.getTemplateList = debounce(this.getTemplateListSource, 200);
    /**
     * 检查流程： 遍历环境,检查是否有进程状态
     * 1、第一次检查，如果不存在进程，则检查module_list（只检查一次），反之结束；
     * 2、module_list检查结束，若有TOPO，则继续做下一个环境的检查，反之结束；
     * 3、若每个环境都没有进程，则做一次同步操作（只操作一次），然后再次遍历环境
     * 4、若遍历之后还是没有进程，则调整状态为 completed 结束
     *
     *  与之前检查流程不同的是
     * 1、无数据的情况下需要把三个环境都检查完
     * 2、每个环境都无进程 则不会调用 getTemplateList 方法
     */

    this.resetEnvList();
    this.checkProcessCount();
  },
  methods: {
    async getTemplateListSource() {
      let result = false;
      try {
        this.isDataLoading = true;
        const query = this.getSearchParams();
        const res = await this.$store.dispatch('process/ajaxGetProcessStatusList', {
          data: {
            page: this.pagination.current,
            pagesize: this.pagination.limit,
            [this.isDropdownMode ? 'scope' : 'expression_scope']: this.selectedScope,
            ...query,
          },
        });
        res.data.list.forEach((item) => {
          item.isSelect = false;
          item.disable = false;
          item.templateCount = item.config_templates.length;
        });
        this.tableData = res.data.list;
        this.pagination.count = res.data.count;
        result = !!res.data.list.length;
      } catch (e) {
        console.warn(e);
      } finally {
        if (this.checkeStatus === 'loading') {
          this.checkeStatus = result ? 'normal' : 'completed';
        }
        this.isDataLoading = false;
      }
    },
    // 获取搜索条件
    async getFilterCondition() {
      const res = await this.$store.dispatch('meta/ajaxGetStatusFilterCondition');
      const filterData = [];
      for (const [key, value] of Object.entries(res.data)) {
        const params = {
          children: value,
          id: key.split('_choices')[0],
        };
        switch (key) {
          case 'process_status_choices':
            params.name = this.$t('进程状态');
            break;
          case 'is_auto_choices':
            params.name = this.$t('托管状态');
            break;
          case 'bk_cloud_id_choices':
            params.multiable = true;
            params.name = this.$t('云区域');
        }
        filterData.push(params);
      }
      filterData.push({
        name: 'IP',
        id: 'bk_host_innerip',
      });
      this.filterData = filterData;
      this.searchSelectData = filterData;
    },
    // 生成搜索参数
    getSearchParams() {
      const params = {};
      const searches = [];
      if (this.searchSelectValue.length) {
        this.searchSelectValue.forEach((item) => {
          const ids = ['bk_cloud_id', 'bk_host_innerip'];
          const idlist = ['process_status', 'is_auto'];
          if (ids.includes(item.id)) {
            params[`${item.id}s`] = item.values.map(val => val.id);
          } else if (idlist.includes(item.id)) {
            params[`${item.id}_list`] = item.values.map(val => val.id);
          } else {
            searches.push(item.id);
            params.searches = searches;
          }
        });
      }
      if (this.ordering) {
        params.ordering = this.ordering;
      }
      // 获取时间
      return params;
    },
    handleSortChange({ prop, order }) {
      if (order === 'ascending') {
        this.ordering = prop;
      } else if (order === 'descending') {
        this.ordering = `-${prop}`;
      } else {
        this.ordering = '';
      }
      this.getTemplateList();
    },
    handlePageLimitChange(val) {
      this.pagination.current = 1;
      this.pagination.limit = val;
      this.getTemplateList();
    },
    handlePageChange(val) {
      this.pagination.current = val;
      this.getTemplateList();
    },
    // 筛选表达式组件返回事件
    valueChange(mode, selectedScope) {
      this.selectedScope = JSON.parse(JSON.stringify(selectedScope));
      this.isDropdownMode = mode;
      this.pagination.current = 1;
      this.getTemplateList();
    },
    onSelectedAllPages(val) {
      this.isSelectedAllPages = val;
      this.processIdList = [];
    },
    handleRowCheck() {
      const processIdList = [];
      this.tableData.forEach((item) => {
        if (item.isSelect) {
          processIdList.push(item.bk_process_id);
        }
      });
      this.processIdList = processIdList;
    },
    handleClearSelection() {
      this.$refs.tableContent.onClearSelectedData();
    },
    // 进程操作
    operateProcess(type, id) {
      this.dialogInfo = {
        title: this.jobAction.find(action => type === action.type).actionName,
        visible: true,
        rowId: id,
        operateType: type,
      };
    },
    // 二次确定允许操作
    async handleDialogConFirm() {
      try {
        this.isDataLoading = true;
        this.selectLength = 0;
        const { rowId, operateType } = this.dialogInfo;
        this.isBtnLoading = rowId ? '' : operateType;
        const params = {
          op_type: operateType,
        };
        // 只有全选与非全选的区别 - 全选: (scope || expression_scope) + 筛选条件, 非全选: scope + process_id
        if (this.isSelectedAllPages) {
          params[this.isDropdownMode ? 'scope' : 'expression_scope'] = this.selectedScope;
          Object.assign(params, this.getSearchParams());
        } else {
          const copySelected = this.$refs.selectInstanceRef.dropdownSelectedData || {};
          const scope = {
            bk_set_env: this.selectedScope.bk_set_env,
          };
          Object.keys(copySelected).forEach((key) => {
            scope[key] = [];
          });
          scope.bk_process_ids = rowId ? [rowId] : [...this.processIdList];
          params.scope = scope;
        }
        const res = await this.$store.dispatch('process/ajaxSetOperateProcess', {
          data: params,
        });
        this.$store.commit('routeTaskHistoryDetail', res.data.job_id);
      } catch (error) {
        console.warn(error);
        this.isBtnLoading = '';
        this.isDataLoading = false;
      }
    },
    // 二次确定取消操作
    handleDialogCancel() {
      this.isBtnLoading = '';
      this.isDataLoading = false;
      this.dialogInfo.visible = false;
      this.dialogInfo.rowId = null;
    },
    // 配置下展开发侧滑面板
    showSideSlider(row) {
      if (this.isDropdownMode) {
        this.selectedScope.bk_process_ids = [row.bk_process_id];
      } else {
        this.selectedScope.bk_process_id = String(row.bk_process_id);
      }
      this.isShow = true;
      this.processDetail = row;
    },
    // 关闭侧滑面板
    closeSideSlider() {
      this.isShow = false;
    },
    // 批量配置下发
    async operateConfigDistribute() {
      const scope = this.$refs.selectInstanceRef.getFormatScope();
      if (!this.isSelectedAllPages) {
        if (this.isDropdownMode) {
          scope.bk_process_ids = [...this.processIdList];
        } else {
          scope.bk_process_id = JSON.stringify(this.processIdList);
        }
      }
      this.$router.push({
        path: '/process-manage/release-config',
        query: {
          scope: JSON.stringify(scope),
          isDropdownMode: this.isDropdownMode,
        },
      });
    },
    // 配置下发
    onConfigDistribute() {
      this.isShow = false;
    },
    // 同步进程
    async synchronousProcess(type) {
      try {
        this.isSynchronousLoading = true;
        this.isDataLoading = true;
        let res;
        if (type === 'status') {
          res = await this.$store.dispatch('process/ajaxSynchProcessStatus');
        } else {
          res = await this.$store.dispatch('process/ajaxFlushProcess');
        }
        if (res.result) {
          // 同步完成之后，再遍历环境检查一次
          if (this.checkeStatus === 'loading') {
            this.hasCheckedAsync = true;
            this.resetEnvList();
            this.checkStepInstance();
          } else {
            if (type === 'config') {
              // 需重新拉取筛选数据
              this.$router.go(0);
            } else if (type === 'status') { // 仅更新表格数据(状态)
              this.handlePageChange(this.pagination.current);
            }
          }
          if (this.showNormalProcess) {
            this.$bkMessage({
              message: this.$t('同步成功'),
              theme: 'success',
            });
          }
        }
      } catch (error) {
        if (this.checkeStatus === 'loading') {
          this.checkeStatus = 'completed';
        }
        console.warn(error);
      } finally {
        this.isSynchronousLoading = false;
        if (type !== 'status') {
          this.isDataLoading = false;
        }
      }
    },
    // 复制逻辑
    handlePaste(e) {
      const [data] = e.clipboardData.items;
      data.getAsString((value) => {
        const { searchSelect } = this.$refs;
        let isIpType = false; // 是否为IP类型
        // 已选择特定类型的情况下 - 保持原有的粘贴行为（排除IP类型的粘贴
        if (searchSelect.input && searchSelect.input.value) {
          const val = searchSelect.input.value;
          isIpType = /ip/i.test(searchSelect.input.value);
          Object.assign(e.target, { innerText: isIpType ? '' : val + value }); // 数据清空或合并
          this.$refs.searchSelect.handleInputChange(e); // 回填并响应数据
          this.$refs.searchSelect.handleInputFocus(e); // contenteditable类型 - 光标移动到最后
        } else {
          isIpType = true;
        }
        if (isIpType) {
          const str = value.replace(/;+|；+|_+|\\+|，+|,+|、+|\s+/g, ',').replace(/,+/g, ' ')
            .trim();
          const splitCode = ['，', ' ', '、', ',', '\n'].find(split => str.indexOf(split) > 0) || '\n';
          const ipRegx = new RegExp('^((25[0-5]|2[0-4]\\d|[01]?\\d\\d?)\\.){3}(25[0-5]|2[0-4]\\d|[01]?\\d\\d?)$');
          const tmpStr = str.trim().split(splitCode);
          const isIp = tmpStr.every(item => ipRegx.test(item));
          if (isIp) {
            this.handlePushValue('bk_host_innerip', tmpStr.map(ip => ({
              id: ip,
              name: ip,
            })));
          } else {
            this.searchSelectValue.push({
              id: str.trim().replace('\n', ''),
              name: str.trim().replace('\n', ''),
            });
          }
        }
      });
    },
    handlePushValue(prop, values, merged = true) {
      if (!values || !Array.isArray(values)) return;
      const index = this.searchSelectValue.findIndex(item => item.id === prop || item.id === this.toLine(prop));
      if (index > -1) {
        const originValues = merged ? this.searchSelectValue[index].values || [] : [];
        values.forEach((value) => {
          const isExist = originValues.some(item => item && item.id === value.id);
          if (!isExist) {
            originValues.push(value);
          }
        });
        this.searchSelectValue[index].values = originValues;
      } else if (prop) {
        const data = this.filterData.find(data => data.id === prop || data.id === this.toLine(prop));
        this.searchSelectValue.push({
          id: prop,
          name: data ? data.name : '',
          values,
        });
      }
    },
    toLine(name) {
      return name.replace(/([A-Z])/g, '_$1').toLowerCase();
    },
    // 处理search select的过滤数据
    handleSearchSelectFilter() {
      const filterData = this.filterData.filter((item) => {
        for (const { id } of this.searchSelectValue) {
          if (item.id === id) {
            return false;
          }
        }
        return true;
      });
      if (!filterData.length && this.isMenuShow) {
        this.$refs.searchSelect.popperMenuInstance.hide();
      }
      this.searchSelectData = filterData;
    },
    handleSearchSelectShowMenu() {
      this.isMenuShow = true;
    },
    /**
             * search select输入框信息变更
             */
    handleSearchSelectChange(list) {
      // 先判断是输入还是删除
      if (list.length > this.prevListLength) {
        this.isMatch = false;
        const lastValue = list[list.length - 1];
        // 内网ip输入处理
        if (lastValue.id === 'bk_host_innerip') {
          this.isMatch = true;
          return;
        }
        // 自定义输入处理
        if (lastValue.id === lastValue.name) {
          this.isMatch = true;
          return;
        }
        const childrenList = this.filterData.find(item => item.id === lastValue.id);
        if (childrenList && childrenList.children) {
          childrenList.children = childrenList.children.map((child) => {
            const searchValue = lastValue.values.find(value => value.name === child.name);
            if (searchValue) {
              child.checked = true;
              searchValue.id = child.id;
              this.isMatch = true;
            } else {
              child.checked = false;
            }
            return child;
          });
        }
      } else {
        this.filterData.forEach((data) => {
          const item = list.find(item => item.id === data.id);
          if (data.children) {
            data.children = data.children.map((child) => {
              if (!item) {
                child.checked = false;
              } else {
                child.checked = item.values.some(value => value.id === child.id);
              }
              return child;
            });
          }
        });
      }
      if (!this.isMatch && list.length) {
        this.searchSelectValue.pop();
        this.$bkMessage({
          message: this.$t('请在列表中选择'),
          theme: 'warning',
        });
      }
      this.prevListLength = this.searchSelectValue.length;
    },
    handleFilterHeaderReset(prop) {
      const index = this.searchSelectValue.findIndex(item => item.id === prop);
      if (index > -1) {
        this.searchSelectValue.splice(index, 1);
      }
    },
    // 表头筛选变更
    handleFilterHeaderConfirm(prop, list) {
      this.isMenuShow = false;
      const index = this.searchSelectValue.findIndex(item => item.id === prop);
      const values = list.reduce((pre, item) => {
        if (item.checked) {
          pre.push({
            id: item.id,
            name: item.name,
          });
        }
        return pre;
      }, []);
      if (index > -1) {
        // 已经存在就覆盖
        this.searchSelectValue[index].values = values;
      } else {
        const data = this.filterData.find(data => data.id === prop);
        // 不存在就添加
        this.searchSelectValue.push({
          id: prop,
          name: data ? data.name : '',
          values,
        });
      }
    },
    // 检查是否有进程
    async checkProcessCount() {
      this.checkeStatus = 'loading';
      this.tableData = [];
      this.isDataLoading = true;
      try {
        this.checkedEnv = this.checkedEnvList.splice(0, 1)[0];
        if (!this.localEnv) {
          this.selectedScope.bk_set_env = this.checkedEnv;
        }
        const res = await this.$store.dispatch('process/ajaxGetProcessStatusList', {
          data: {
            page: 1,
            pagesize: 10,
            scope: { bk_set_env: this.checkedEnv },
          },
        });
        if (res.data.list && res.data.list.length) {
          this.checkeStatus = 'normal';
        } else {
          this.checkStepInstance();
        }
      } catch (e) {
        this.checkeStatus = 'unknow';
        console.warn(e);
      } finally {
        if (this.showNormalProcess) {
          this.isDataLoading = false;
        }
      }
    },
    // 检查实例状态
    async checkStepInstance() {
      if (this.checkeStatus !== 'loading') return;
      if (!this.hasCheckedModelList) {
        try {
          const res = await this.$store.dispatch('cmdb/ajaxGetModuleListBySet', {
            data: { bk_set_ids: [] },
          });
          this.hasCheckedModelList = true;
          if (res.data && res.data.length) {
            // 进行下一个环境的检查操作
            this.checkProcessCount();
          } else {
            this.checkeStatus = 'error';
          }
        } catch (e) {
          console.warn(e);
          this.isDataLoading = false;
          this.checkeStatus = 'error';
        }
      } else {
        // 如果还剩下环境没有检查， 那么先检查完，否则同步之后再遍历环境做检查
        if (this.checkedEnvList.length) {
          this.checkProcessCount();
        } else {
          // 如果没有同步，做一次同步操作, 否则结束检查
          if (!this.hasCheckedAsync) {
            this.synchronousProcess();
          } else {
            // （module_list检查通过才可能到这一步，所以一定是'completed'）
            this.checkeStatus = 'completed';
          }
        }
      }
    },
    // 确定环境检查的顺序, 如果手动选择过环境，则始终保持选中
    resetEnvList() {
      const { bizId } = this.$store.state;
      const bizEnvMap = JSON.parse(window.localStorage.getItem('BK_SET_ENV_MAP') || '{}');
      const setEnv = bizEnvMap[bizId];
      const list = [];
      const commonOrderlist = ['3', '2', '1'];
      if (setEnv) {
        const index = commonOrderlist.findIndex(env => env === setEnv);
        if (index > -1) {
          this.localEnv = setEnv;
          this.selectedScope.bk_set_env = setEnv;
          list.push(setEnv);
          commonOrderlist.splice(index, 1);
        }
      }
      this.checkedEnvList = list.concat(commonOrderlist);
    },
    handleTableClear() {
      this.isDataLoading = true;
      bus.$emit('clear-select-filter');
      this.searchSelectValue = [];
      this.handleSearchSelectChange([]);
    },
  },
};
</script>

<style lang="postcss" scoped>
  .process-status {
    height: 100%;

    .process-status-title {
      font-size: 16px;
      color: #313238;
      margin-bottom: 20px;
    }

    .search-content {
      display: flex;
      align-items: center;
      justify-content: space-between;

      /deep/ .select-instance-container {
        flex: 2.5 0;
        padding-left: 0;
        padding-right: 0;

        .dropdown-selector-container,
        .expression-input-container {
          flex: 1 1;
        }

        .king-select-env {
          background-color: #f5f6fa;
        }
      }

      .search-select-input-container {
        flex: 1 0;
        width: 302px;
        max-width: 500px;
        margin-left: 40px;

        /deep/ .search-select-wrap {
          background-color: #fff;
        }
      }
    }

    .selected-all-pages {
      height: 30px;
      line-height: 30px;
      text-align: center;
      background: #ebecf0;
      color: #63656e;
      font-size: 12px;
      margin-bottom: 6px;

      .count {
        color: #666871;
        font-weight: 700;
      }
    }
  }
</style>
