<template>
  <div class="process-attribute-container" v-bkloading="{ isLoading: loading }">
    <div class="page-head">{{ $t('进程属性') }}</div>
    <EmptyProcess v-if="isEmtpyTopo" empty-type="topo"></EmptyProcess>
    <div class="page-content" v-show="!loading && !isEmtpyTopo">

      <section
        :class="['content-left', { 'width-transition': !drag.isMouseDown }]"
        :style="{ width: `${targetWidth}px` }">
        <div class="process-topo">
          <ProcessTarget
            ref="processTarget"
            class="process-topo-content"
            v-model="tabActive"
            :loading="!loading && topoLoading"
            :tree-data="topoData"
            :template-list="templateList"
            @format-tree="handleUpdateTree"
            @tree-selected="handleTargetSelected"
            @temp-selected="handleTargetSelected"
            @tab-change="handleTabChange"
            @empty-clear="emptySearchClear">
          </ProcessTarget>
        </div>
        <div class="drag-box">
          <div ref="dragBorder" id="drag-border" class="drag-border"></div>
        </div>
        <div class="topo-toggle" @click.stop="showLeftTopo = !showLeftTopo">
          <i :class="['gsekit-icon gsekit-icon-angle-left-line', { 'show-topo': !showLeftTopo }]"></i>
        </div>
      </section>

      <section class="content-right">
        <EmptyServiceBox v-if="isTemplateTab && isEmtpyTemplate" type="template" @click-link="handleEmptyLink">
        </EmptyServiceBox>
        <!-- <EmptyServiceBox v-else-if="isShowTopoTree && isEmtpyInstance" type="instance" :info="emptyInstanceInfo">
        </EmptyServiceBox> -->

        <template v-else>
          <section class="temp-head" v-if="isTemplateTab">
            <p class="title"><span class="tag">{{ $t('模版') }}</span>{{ selectedTemp.name }}</p>
          </section>
          <section class="topo-head" v-else>
            <p class="topo-path text-overflow-row" v-bk-overflow-tips>{{ topoProcessTitle }}</p>
            <h2 class="topo-name text-overflow-row mt10" v-bk-overflow-tips>{{ selectedNode.topoName }}</h2>
          </section>
          <div class="head-tips" v-if="isTemplateTab && showSyncTip">
            <i class="gsekit-icon gsekit-icon-swither-small tips-icon"></i>
            <span class="tips-text">{{ $t('当前服务模板下进程属性已改变，需到配置平台进行同步操作方可生效。') }}</span>
            <bk-button class="ml20" text size="small" @click="goSyncTemplate">{{ $t('去同步') }}</bk-button>
            <span style="flex: 1"></span>
          </div>

          <section class="content-operate">
            <div></div>
            <!-- 支持搜索：进程别名、进程名称、所属拓扑、配置缺失情况（这里需要固定值：基础控制配置、启动配置、停止配置、重启配置、重载配置、强制终止配置 -->
            <!-- 配置缺失情况，按大类别来搜索，不需要支持展开后每个字段的搜索 -->
            <bk-search-select
              class="search-input"
              ref="searchSelect"
              v-test.common="'searchSelect'"
              :placeholder="$t('进程别名、进程名称、配置缺失情况')"
              :show-condition="false"
              :data="filterSearchSelectData"
              v-model="searchSelectValue"
              @change="handleSearchSelectChange">
            </bk-search-select>
          </section>

          <section
            class="content-table-block"
            v-bkloading="{ isLoading: !loading && tableLoading }">
            <ProcessTable
              v-if="!tableLoading"
              :loading="!loading && tableLoading"
              :is-biz-process="!isTemplateTab"
              :static-total="pagination.count"
              :static-incomplete="staticIncomplete"
              :table-head="tableHead"
              :table-data="tableData"
              :selections="selections"
              :not-editable="notEditable"
              :pagination="pagination"
              :selected-node="isTemplateTab ? selectedTemp : selectedNode"
              :edit-rules="editRules"
              :is-search="!!searchSelectValue.length"
              :empty-type="tableEmptyType"
              @cell-edit="handleCellEdit"
              @eidt-disabled="handleEidtDisabled"
              @sub-head-filter="handSubHeadFilter"
              @change-filters="handleFiltersChange"
              @page-change="handlePageChange"
              @selection-change="handleTableSelected"
              @empty-clear="emptySearchClear">
            </ProcessTable>
          </section>

          <!-- <bk-sideslider
            ext-cls="process-edit-slider" :is-show.sync="slider.show" :title="slider.title" :width="slider.width">
            <template slot="content">
              <ProcessSliderEidt
                v-if="selections.length"
                :selections="selections"
                :prop-list="propList"
                @cancel-edit="slider.show = false">
              </ProcessSliderEidt>
            </template>
          </bk-sideslider> -->
        </template>
      </section>
    </div>

  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import ProcessTarget from '@/components/ProcessTarget/index';
import ProcessTable from './ProcessTable';
import EmptyProcess from '@/components/Empty/EmptyProcess';
import EmptyServiceBox from '@/components/Empty/EmptyServiceBox';
// import ProcessSliderEidt from './ProcessSliderEdit'
import rules from './attributeEditRule';
import { sortByCustom } from '@/common/util';
import { Drag } from './drag';

export default {
  name: 'ProcessAttribute',
  components: {
    ProcessTarget,
    ProcessTable,
    EmptyProcess,
    EmptyServiceBox,
    // ProcessSliderEidt
  },
  props: {
    type: {
      type: String,
      default: 'template', // node || template
    },
  },
  data() {
    return {
      isEmtpyTopo: false, // 展示空topo页
      isEmtpyTemplate: false, // 展示空模板页
      isEmtpyInstance: false, // 展示空实例页
      loading: false,
      topoLoading: false,
      tableLoading: false,
      showLeftTopo: true,
      leftWidth: 330,
      isMouseDown: true,
      showSyncTip: false,
      tabActive: 'template', // node || template-前端分页 && 前端搜索
      selectedNode: {},
      selectedTemp: {},
      nodeInfo: {
        type: '',
        id: '',
        instanceId: null,
      },
      templateId: null,
      instanceId: null,
      searchSelectData: [
        { name: this.$t('进程别名'), id: 'bk_process_name' },
        { name: this.$t('进程名称'), id: 'bk_func_name' },
        {
          name: this.$t('配置缺失'),
          id: 'missing',
          multiable: true,
          // 'width': 180,
          // 'align': 'right'
          children: [
            { name: this.$t('基础控制配置'), id: 'controlBase' },
            { name: this.$t('启动配置'), id: 'startConfig' },
            { name: this.$t('停止配置'), id: 'stopConfig' },
            { name: this.$t('重启配置'), id: 'restartConfig' },
            { name: this.$t('重载配置'), id: 'reloadConfig' },
            { name: this.$t('强制终止配置'), id: 'faceStopConfig' },
          ],
        },
      ],
      searchSelectValue: [],
      staticIncomplete: 0, // 缺失数
      topoData: [],
      formatTree: [],
      templateList: [],
      sourceTableData: [],
      tableData: [],
      selections: [],
      pagination: {
        current: 1,
        count: 0,
        limit: 10,
      },
      slider: {
        show: false,
        title: this.$t('批量编辑'),
        width: 756,
      },
      // 需要保证顺序与表格一致
      filterFields: [],
      tableHead: [
        {
          label: '',
          props: 'base',
          key: '',
          fixed: true,
          computed: true,
          // width: 120, // 组件宽度计算不准确，人肉计算已固定fixed宽度总和
          isExpandable: false, // 是否可展开
          isExpand: true, // 是否展开
          hasUndone: false,
          hasChild: true,
          headerAlign: 'center',
          child: [
            { label: this.$t('进程别名'), prop: 'bk_process_name', computed: true, slotNameStr: 'alias', fixed: true, showOverflowTooltip: true },
          ],
        },
        {
          label: this.$t('进程基本属性'),
          props: 'base',
          key: 'attributeBase',
          isExpandable: false,
          isExpand: true,
          hasUndone: false,
          hasChild: true,
          headerAlign: 'center',
          child: [
            { label: this.$t('进程名称'), prop: 'bk_func_name', fixed: false, computed: true, showOverflowTooltip: true },
            { label: this.$t('所属拓扑'), prop: 'topoPath', fixed: false, slotNameStr: 'topo', minWidth: 200, showOverflowTooltip: true },
            { label: this.$t('进程启动参数'), prop: 'bk_start_param_regex', minWidth: 200, fixed: false, showOverflowTooltip: true }, // renderHeader: this.tipsRenderHeader },
            { label: this.$t('进程备注'), prop: 'description', fixed: false, computed: true, showOverflowTooltip: true }, // ,  renderHeader: this.tipsRenderHeader }
          ],
        },
        {
          label: this.$t('基础控制配置'),
          props: '',
          key: 'controlBase',
          isExpandable: true,
          isExpand: true,
          fixed: false,
          computed: true,
          hasUndone: false,
          hasChild: true,
          tips: this.$t('若要使用Gsekit进行进程管理，需完善此基础控制配置', [window.PROJECT_CONFIG.APP_NAME]),
          child: [
            { label: this.$t('启动用户'), prop: 'user', computed: true, fixed: false, showOverflowTooltip: true },
            { label: this.$t('PID 文件路径'), prop: 'pid_file', minWidth: 200, fixed: false, showOverflowTooltip: true },
            { label: this.$t('工作路径'), prop: 'work_path', minWidth: 160, fixed: false, showOverflowTooltip: true },
            { label: this.$t('操作超时时长th'), prop: 'timeout', type: 'number', minWidth: 120, fixed: false, showOverflowTooltip: true },
            { label: this.$t('启动优先级'), prop: 'priority', computed: true, minWidth: 100, fixed: false },
          ],
        },
        {
          label: this.$t('启动配置'),
          props: '',
          key: 'startConfig',
          minWidth: 100,
          isExpandable: true,
          isExpand: true,
          fixed: false,
          hasUndone: false,
          hasChild: true,
          child: [
            { label: this.$t('启动命令'), prop: 'start_cmd', minWidth: 140, fixed: false, showOverflowTooltip: true, showOverflowTooltip: true },
            { label: this.$t('启动等待时长th'), prop: 'bk_start_check_secs', type: 'number', minWidth: 130, fixed: false },
            { label: this.$t('启动数量'), prop: 'proc_num', type: 'number', minWidth: 100, fixed: false },
          ],
        },
        {
          label: this.$t('停止配置'),
          props: '',
          key: 'stopConfig',
          computed: true,
          isExpandable: true,
          isExpand: true,
          fixed: false,
          hasUndone: false,
          hasChild: true,
          child: [
            { label: this.$t('停止命令'), prop: 'stop_cmd', computed: true, fixed: false, showoverflowtooltip: true, showOverflowTooltip: true },
          ],
        },
        {
          label: this.$t('重启配置'),
          props: '',
          key: 'restartConfig',
          computed: true,
          isExpandable: true,
          isExpand: true,
          fixed: false,
          hasUndone: 0,
          hasChild: true,
          child: [
            { label: this.$t('重启命令'), prop: 'restart_cmd', computed: true, fixed: false, showOverflowTooltip: true },
          ],
        },
        {
          label: this.$t('重载配置'),
          props: '',
          key: 'reloadConfig',
          isExpandable: true,
          isExpand: true,
          computed: true,
          fixed: false,
          hasUndone: false,
          hasChild: true,
          child: [
            { label: this.$t('重载命令'), prop: 'reload_cmd', computed: true, fixed: false, showOverflowTooltip: true },
          ],
        },
        {
          label: this.$t('强制终止配置'),
          props: '',
          key: 'faceStopConfig',
          width: 'auto',
          isExpandable: true,
          isExpand: true,
          fixed: false,
          hasUndone: false,
          computed: true,
          hasChild: true,
          child: [
            { label: this.$t('强制停止命令'), prop: 'face_stop_cmd', computed: true,  fixed: false, showOverflowTooltip: true },
          ],
        },
      ],
      editRules: rules,
      // 二级head的提示 目前没有比较简洁的方法，先放这儿
      // subHeadMap: {
      //     startParams: this.$t('进程启动参数Tips'),
      //     remarks: this.$t('进程备注Tips')
      // },
      notEditable: ['selection', 'isTemplate', 'bk_func_name', 'bk_process_name', 'alias', 'name', 'topo'],
      // propList: [],
      drag: {},
    };
  },
  computed: {
    ...mapState(['bizId']),
    targetWidth() {
      return this.showLeftTopo ? this.leftWidth : 0;
    },
    topoPath() {
      return this.selectedNode.topoConcatPath;
    },
    topoProcessTitle() {
      return this.topoPath ? `${this.topoPath}` : this.$store.state.bizName;
    },
    batchDisabled() {
      return !this.selections.length;
    },
    isTemplateTab() {
      return this.tabActive === 'template';
    },
    filterSearchSelectData() {
      const ids = this.searchSelectValue.map(item => item.id);
      return this.searchSelectData.filter(item => !ids.includes(item.id));
    },
    tableEmptyType() {
      return !!this.searchSelectValue.length ? 'search-empty' : 'empty';
    },
  },
  watch: {
    $route: {
      deep: true,
      handler(newVale, old) {
        const { biz: oldBiz } = old.query;
        const { biz: newBiz, template } = newVale.query;
        this.templateId = template || null;
        this.tabActive = this.type;
        Object.assign(this.pagination, {
          current: 1,
          count: 0,
          limit: 10,
        });
        this.setTableHead();
        if (oldBiz !== newBiz) {
          this.initTopoAndRouter();
        } else {
          this.initTargetInfo();
        }
      },
    },
  },
  created() {
    this.computedColumnsWidth();
    this.initTopoAndRouter();
  },
  mounted() {
    this.$nextTick(() => {
      this.drag = new Drag(this.$refs.dragBorder, 'right', this.handleDrag, true);
    });
  },
  methods: {
    ...mapActions('cmdb', ['ajaxGetProcessRelated', 'ajaxGetCheckServiceTemplate', 'ajaxGetBatchCheckServiceTemplate']),
    ...mapActions('process', ['ajaxGetTemplateProcessByServiceTemplate']),
    // 初始化页面 topo template router
    initTopoAndRouter() {
      this.loading = true;
      this.initTableHead();
      this.loadTopoData().then((res) => {
        if (res) {
          this.initTargetInfo();
        } else {
          this.loading = false;
        }
      });
    },
    async initTargetInfo() {
      const { node = '', template } = this.$route.query || {};
      this.tabActive = ['template', 'node'].includes(this.type) ? this.type : 'template';
      const templateId = template - 0;
      // 判断 query 是否在 模板 或 topo 里
      if (this.isEmtpyTopo || (this.tabActive === 'template' && this.isEmtpyTemplate)) {
        this.loading = false;
        return false;
      }

      if (this.tabActive === 'template') {
        const currentTemp = this.templateList.find(item => item.id === templateId) || this.templateList[0];
        if (currentTemp.id === templateId) {
          this.selectedTemp = currentTemp;
          this.templateId = currentTemp.id;
          this.$refs.processTarget.handleSetTemplateActive(currentTemp);
        } else {
          this.$store.commit('routeProcessAttr', {
            params: { type: this.tabActive },
            query: { template: currentTemp.id },
          });
          return false;
        }
      } else {
        const select = { nodeItem: null };
        if (node) {
          const arr = node.split('-'); // 0-type 1-id 2-instanceId instanceId暂时不做处理
          if (arr[2]) {
            this.findSelectedTopo({ type: 'serviceInstance', id: arr[2] - 0 }, select, this.formatTree);
            if (!select.nodeItem) {
              this.$store.commit('routeProcessAttr', {
                params: { type: this.tabActive },
                query: { node: `${arr[0]}-${arr[1]}` },
              });
            }
          }
          if (!select.nodeItem) {
            this.findSelectedTopo({ type: arr[0], id: arr[1] - 0 }, select, this.formatTree);
          }
        }
        if (!node || !select.nodeItem) {
          const { bk_obj_id: bkObjId, bk_inst_id: bkInstId } = this.formatTree[0];
          this.$store.commit('routeProcessAttr', {
            params: { type: this.tabActive },
            query: { node: `${bkObjId}-${bkInstId}` },
          });
          return false;
        }
        this.selectedNode = select.nodeItem;
        this.$refs.processTarget.handleSetTopoActive(select.nodeItem.uuid);
      }
      this.pageLoadProcess();
      this.loading = false;
    },
    findSelectedTopo({ type, id }, obj, list) {
      list.forEach((item) => {
        if (type === 'serviceInstance') {
          if (item.service_instance_id === id) {
            obj.nodeItem = item;
          }
        } else {
          if (item.bk_inst_id === id && type === item.bk_obj_id) {
            obj.nodeItem = item;
            if (type === 'biz') {
              item.topoExpand = true;
            }
          }
        }
        if (item.child && item.child.length) {
          this.findSelectedTopo({ type, id }, obj, item.child);
        }
      });
    },
    // 页面加载流程
    async pageLoadProcess() {
      if (this.isTemplateTab) {
        if (this.templateId) {
          this.loadTableData();
          this.checkServeTemplate();
          this.batchCheckServeTemplate();
        } else {
          this.initTargetInfo();
        }
      } else {
        this.loadTableData();
        this.loadUndoneCount();
      }
    },
    async loadTopoData() {
      return new Promise(async (resolve, reject) => {
        try {
          this.topoLoading = true;
          const [topoRes, templateRes] = await Promise.all([
            this.$store.dispatch('cmdb/ajaxGetBizTopo'),
            this.$store.dispatch('cmdb/ajaxGetServiceTemplate'),
          ]);
          templateRes.data.forEach((item) => {
            item.active = false;
            item.visible = true;
            item.showSync = false;
          });
          templateRes.data.sort(sortByCustom('name'));
          this.templateList = templateRes.data;
          this.isEmtpyTemplate = !templateRes.data || !templateRes.data.length;
          if (topoRes.data && topoRes.data.length) {
            this.topoData = topoRes.data;
            this.isEmtpyTopo = !(topoRes.data[0].child && topoRes.data[0].child.length);
          } else {
            this.isEmtpyTopo = true;
          }
          resolve(!this.isEmtpyTopo || (this.type === 'template' && !this.isEmtpyTemplate));
        } catch (e) {
          console.warn(e);
          this.loading = false;
          reject(e);
        } finally {
          this.topoLoading = false;
        }
      });
    },
    async loadTableData() {
      let tableCount = 0;
      let data = [];
      try {
        this.tableLoading = true;
        const methodName = this.isTemplateTab ? 'ajaxGetTemplateProcessByServiceTemplate' : 'ajaxGetProcessRelated';
        const res = await this[methodName](this.isTemplateTab ? { serviceTemplateId: this.templateId } : this.getParams('load'));
        if (res.result) {
          if (this.type === 'template') {
            data = res.data.map(item => ({
              ...item,
              ...(item.property || {}),
            }));
            this.sourceTableData = data;
            tableCount = res.data.length;
            data = this.forntfilterData();
          } else {
            const { count, info = [] } = res.data;
            data = info.map((item) => {
              const { host, module: modules, process, process_template, service_instance, set } = item;
              return {
                ...item,
                ...host,
                ...modules,
                ...process,
                ...set,
                processTemplateId: process_template.id,
                serviceInstanceId: service_instance.id,
                topoPath: this.setRowTopoPath(set, modules, service_instance),
                disabled: !this.isTemplateTab && !!process_template.id,
                showTypeTag: !this.isTemplateTab,
                isTemplate: !!process_template.id,
              };
            });
            tableCount = count;
          }
        }
      } catch (e) {
        console.warn(e);
      } finally {
        // 设置表头状态
        this.setHeadUndoneStatus(data);
        this.tableData.splice(0, this.tableData.length, ...data);
        this.pagination.count = tableCount;
        this.tableLoading = false;
        this.loading = false;
        if (this.isTemplateTab) {
          this.staticIncomplete = this.getUndoneCount();
        }
      }
    },
    // 加载未完成的数量
    async loadUndoneCount() {
      const params = this.getParams('statis');
      const res = await this.ajaxGetProcessRelated(params);
      let count = 0;
      if (res.result) {
        count = res.data.count || 0;
      }
      this.staticIncomplete = count;
    },
    getUndoneCount() {
      const undoneHead = this.tableHead.filter(head => head.isExpandable);
      const undoneKeys = [];
      undoneHead.forEach((item) => {
        undoneKeys.push(...item.child.map(item => item.prop));
      });
      if (!undoneKeys.length) return 0;
      const hasUndoneRows = this.tableData.filter(row => undoneKeys.some(key => row[key] !== 0 && !row[key]));
      return hasUndoneRows.length;
    },
    // 分两张种情况: 正常加载 - load | 缺失统计 - statis | 前端筛选 - front
    getParams(type = 'load') {
      if (type === 'load' && this.type === 'template') {
        return { serviceTemplateId: this.templateId };
      }
      const { current, limit } = this.pagination;
      const params = {
        page: {
          limit,
          // sort: this.filterFields.join(',')
        },
        // field: [], // 暂时统一为空
        // process_property_filter: {}
      };
      if (type === 'statis') {
        params.page.limit = 1; // 仅筛选有效
        const filterRule = [];
        this.filterFields.forEach((field) => {
          filterRule.push({ field, operator: 'equal', value: '' });
          filterRule.push({ field, operator: 'is_null' });
        });
        params.process_property_filter = {
          condition: 'OR', // 模糊匹配 用AND 例如  field, operator: 'equal', value: 'aaaa' }
          rules: filterRule,
        };
      } else { // 正常加载所需条件
        params.page.start = (current - 1) * limit;
        params.page.sort = this.filterFields.join(',');
        if (this.searchSelectValue.length) {
          const undoneRule = []; // 或
          const blurryRule = []; // 且
          const queryRule = []; // 或（同时模糊搜索 进程别名、进程名称）
          // 有模糊匹配 和 配置缺失同时存在的情况
          this.searchSelectValue.forEach((item) => {
            if (item.id === 'missing') {
              item.values.forEach((option) => {
                const head = this.tableHead.find(parent => parent.key === option.id);
                if (head) {
                  head.child.map(child => child.prop).forEach((field) => {
                    undoneRule.push({ field, operator: 'equal', value: '' });
                    undoneRule.push({ field, operator: 'is_null' });
                  });
                }
              });
            } else if (['bk_func_name', 'bk_process_name'].includes(item.id)) {
              blurryRule.push({
                field: item.id,
                operator: 'equal',
                value: item.values.map(option => option.name).join(','),
              });
            } else { // 无固定类型的query 放入进程别名、进程名称下过滤
              const rules = ['bk_func_name', 'bk_process_name'].map(field => ({ field, operator: 'equal', value: item.id }));
              queryRule.push(...rules);
              blurryRule.push({ condition: 'OR', rules });
            }
          });
          if (type === 'load') {
            if (blurryRule.length) {
              if (undoneRule.length) {
                blurryRule.push({
                  condition: 'OR',
                  rules: undoneRule,
                });
              }
              params.process_property_filter = {
                condition: 'AND',
                rules: blurryRule,
              };
            } else {
              params.process_property_filter = {
                condition: 'OR',
                rules: undoneRule,
              };
            }
          } else { // 前端搜索条件
            params.undoneRule = undoneRule;
            params.blurryRule = blurryRule;
            params.queryRule = queryRule;
          }
        }
      }
      const {
        bk_inst_id: bkInstId,
        bk_obj_id: bkObjId,
        topoType,
        service_instance_id: serviceInstanceId,
      } = this.selectedNode;
      if (bkObjId) {
        if (bkObjId === 'set') {
          params.set = {
            bk_set_ids: [bkInstId],
          };
        } else if (bkObjId === 'module') {
          params.module = {
            bk_module_ids: [bkInstId],
          };
        }
      }
      if (topoType && topoType === 'serviceInstance') {
        params.service_instance = {
          ids: [serviceInstanceId],
        };
      }
      return params;
    },
    handleTargetSelected(targetObj) {
      let type = 'template';
      const query = {};
      if (this.isTemplateTab) {
        this.selectedTemp = targetObj;
        this.templateId = targetObj.id;
        query.template = targetObj.id;
      } else {
        type = 'node';
        this.selectedNode = targetObj;
        const { topoParent, bk_inst_id: bkInstId, topoType, service_instance_id: serviceInstanceId } = targetObj;
        let nodeType = topoType;
        let id = bkInstId;
        nodeType = targetObj.bk_obj_id || topoType;
        if (topoType === 'serviceInstance') {
          nodeType = 'module';
          id = `${topoParent.bk_inst_id}-${serviceInstanceId}`;
        }
        query.node = `${nodeType}-${id}`;
      }
      this.$router.replace({
        name: 'process-attr',
        params: { type },
        query,
      });
    },
    handleTabChange(type) {
      this.tabActive = type;
      this.selections = [];
      this.searchSelectValue = [];
      const query = {};
      if (this.isTemplateTab) {
        this.templateId = this.templateList.length ? this.templateList[0].id : null;
        if (this.templateId) {
          query.template = this.templateId;
        }
        this.setNodesExpanded(this.formatTree);
      }
      this.$store.commit('routeProcessAttr', {
        params: { type: this.tabActive },
        query,
      });
    },
    // 检查模板是否需要同步
    async checkServeTemplate() {
      let showSync = false;
      try {
        const hasId = this.isTemplateTab ? !!this.templateId : this.selectedNode.topoType === 'serviceTemplate';
        const serviceTemplateId = this.isTemplateTab ? this.templateId : this.selectedNode.service_template_id;
        if (hasId && serviceTemplateId) {
          const res = await this.ajaxGetCheckServiceTemplate({
            service_template_id: serviceTemplateId,
          });
          if (res.result) {
            showSync = res.data;
          }
        }
      } catch (e) {
        console.warn(e);
      } finally {
        this.showSyncTip = showSync;
      }
    },
    // 批量检查模板是否需要同步 - 比较慢(用于模板列表上同步icon)
    async batchCheckServeTemplate() {
      const res = await this.ajaxGetBatchCheckServiceTemplate();
      if (res.result && res.data && res.data.length) {
        const statusMap = {};
        res.data.reduce((obj, item) => {
          Object.assign(obj, item);
          return obj;
        }, statusMap);
        Object.keys(statusMap).forEach((id) => {
          const template = this.templateList.find(item => `${item.id}` === `${id}`);
          if (template) {
            template.showSync = statusMap[id];
          }
        });
      }
    },
    handleSearchSelectChange() {
      this.handlePageChange({ page: 1 });
    },
    emptySearchClear() {
      this.topoLoading = true;
      this.searchSelectValue = [];
      this.handleSearchSelectChange();
      this.topoLoading = false;
    },
    async handleCellEdit({ row, prop, value }) {
      try {
        let filedList = [];
        this.tableHead.forEach((parent) => {
          filedList = filedList.concat(parent.child.map(item => item.prop));
        });
        // 对比找出来的值
        const excluded = ['selection', 'topoPath'];
        const adscititious = ['create_time', 'last_time', 'bind_info', 'auto_start', 'bk_process_id', 'bk_biz_id', 'bk_supplier_account'];
        filedList = filedList.concat(adscititious);
        const formData = {};
        filedList.reduce((obj, key) => {
          if (!excluded.includes(key)) {
            obj[key] = row[key];
          }
          return obj;
        }, formData);
        const res = await this.$store.dispatch(`process/${this.isTemplateTab ? 'ajaxUpdateProcessTemplate' : 'ajaxUpdateProcessInstance'}`, {
          data: {
            process_template_id: this.isTemplateTab ? row.process_template_id : '',
            process_property: Object.assign(formData, { [prop]: value }),
          },
        });
        if (res.result) {
          row[prop] = value;
          if (this.isTemplateTab) {
            this.showSyncTip = true;
            this.setTemplateServeSync();
          }
          this.setHeadUndoneStatus(this.tableData);
          this.$bkMessage({
            message: this.$t('编辑成功'),
            theme: 'success',
          });
        }
      } catch (error) {
        console.warn(error);
      }
    },
    // 数字、表头筛选
    handleFiltersChange() {
      const undoneFilter = this.searchSelectData.find(item => item.id === 'missing');
      if (undoneFilter) {
        this.searchSelectValue.splice(0, this.searchSelectValue.length, {
          id: undoneFilter.id,
          multiable: undoneFilter.multiable,
          name: undoneFilter.name,
          values: undoneFilter.children.map(item => ({ ...item })),
        });
        this.handlePageChange({ page: 1 });
      }
    },
    handlePageChange({ page, limit }) {
      Object.assign(this.pagination, {
        current: page || 1,
        limit: limit || this.pagination.limit,
      });
      if (this.isTemplateTab) {
        this.tableData = this.forntfilterData();
      } else {
        this.loadTableData();
      }
    },
    handleTableSelected(selections) {
      this.selections = selections;
    },
    handSubHeadFilter({ parent }) {
      this.searchSelectValue.splice(0, this.searchSelectValue.length, {
        id: 'missing',
        multiable: true,
        name: this.$t('配置缺失'),
        values: [
          { id: parent.key, name: parent.label },
        ],
      });
      this.handlePageChange({ page: 1 });
    },
    // 初始化表头
    initTableHead() {
      // this.propList.splice(0, this.propList.length)
      let filterFields = [];
      this.tableHead.forEach((parent, index) => {
        parent.isExpand = !parent.isExpandable || index <= 1;
        if (parent.isExpandable) {
          filterFields = filterFields.concat(parent.child.map(item => item.prop));
        }
        parent.child.forEach((head) => {
          head.editAble = !this.notEditable.includes(head.prop);
          // this.propList.push({
          //     id: head.prop,
          //     name: head.label || head.prop,
          //     disabled: !head.editAble,
          //     multiable: false
          // })
        });
      });
      this.filterFields = filterFields;
      this.setTableHead();
    },
    handleDrag({ x }) {
      if (this.showLeftTopo) {
        if (this.leftWidth + x < 230) {
          this.leftWidth = 230;
        } else if (this.leftWidth + x > 630) {
          this.leftWidth = 630;
        } else {
          this.leftWidth = this.leftWidth + x;
        }
      }
    },
    setHeadUndoneStatus(data = []) {
      const { length } = data;
      this.tableHead.forEach((head) => {
        if (head.isExpandable) {
          let hasUndone = false;
          if (length) {
            data.forEach((row) => {
              if (head.child.some(child => !row[child.prop] && row[child.prop] !== 0)) {
                hasUndone = true;
              }
            });
          }
          head.hasUndone = hasUndone;
        }
      });
    },
    setRowTopoPath(set = {}, modules = {}, serviceInstance = {}) {
      const { bk_set_name: setName = '' } = set;
      const { bk_module_name: moduleName = '' } = modules;
      const { name = '' } = serviceInstance;
      const path = [setName, moduleName, name].filter(item => !!item);
      return path.join('/');
    },
    // 设置 进程
    setTableHead() {
      const isTemplate = this.type === 'template';
      let fixedWidth = this.$textTool.getHeadWidth(this.tableHead[0].child[0].label);
      fixedWidth += isTemplate ? 0 : 70;
      this.tableHead[0].width = fixedWidth;
      this.tableHead[0].child[0].width = fixedWidth;
      // template 不需要 所属topo 硬编码
      const { prop } = this.tableHead[1].child[1];
      if (isTemplate && prop === 'topoPath') {
        this.tableHead[1].child.splice(1, 1);
      }
      if (!isTemplate && prop !== 'topoPath') {
        this.tableHead[1].child.splice(1, 0, {
          label: this.$t('所属拓扑'),
          prop: 'topoPath',
          fixed: false,
          slotNameStr: 'topo',
          minWidth: 200,
          showOverflowTooltip: true,
        });
      }
    },
    goSyncTemplate() {
      const cmdbUrl = window.PROJECT_CONFIG.CMDB_URL;
      const { bizId } = this.$store.state;
      const serviceTemplateId = this.isTemplateTab ? this.selectedTemp.id : this.selectedNode.service_template_id;
      window.open(`${cmdbUrl}/#/business/${bizId}/service/operational/template/${serviceTemplateId}?tab=instance`);
    },
    // 前端筛选 & 分页
    forntfilterData() {
      let data = [...this.sourceTableData];
      const { page, undoneRule, blurryRule, queryRule } = this.getParams('front');
      // 且
      if (queryRule && queryRule.length) {
        data = data.filter(item => queryRule.some(rule => item[rule.field].includes(rule.value)));
      }
      if (blurryRule && blurryRule.length) {
        const filterBlurryRule = blurryRule.filter(rule => rule.field);
        data = data.filter(item => filterBlurryRule.every(rule => item[rule.field].includes(rule.value)));
      }
      // 或
      if (undoneRule && undoneRule.length) {
        data = data.filter(item => undoneRule.some(rule => !item[rule.field]));
      }
      data = data.slice(page.start, page.start + page.limit);
      return data;
    },
    handleUpdateTree(list) {
      this.formatTree = list;
    },
    setTemplateServeSync(id) {
      const tempId = id || this.templateId;
      const temp = this.templateList.find(item => item.id === tempId);
      if (temp) {
        temp.sync = true;
      }
    },
    setNodesExpanded(nodes) {
      nodes.forEach((node) => {
        node.topoExpand = false;
        if (node.child && node.child.length) {
          this.setNodesExpanded(node.child);
        }
      });
    },
    handleEidtDisabled() {
      this.$store.commit('routeProcessAttr', {
        params: { type: 'template' },
        query: { template: this.selectedNode ? this.selectedNode.service_template_id : null },
      });
    },
    // tipsRenderHeader(h, { column }) {
    //   return <span class="text-has-tips" v-bk-tooltips={ this.subHeadMap[column.property] }>{ column.label }</span>
    // },
    handleEmptyLink() {
      const url = `${window.PROJECT_CONFIG.CMDB_URL}/#/business/${this.$store.state.bizId}/service/template/create`;
      window.open(url, '_blank');
    },
    computedColumnsWidth(columns, parent) {
      const list = columns || this.tableHead;
      list.forEach((item) => {
        if (item.computed) {
          item.minWidth = Math.max(parent?.minWidth || 0, this.$textTool.getHeadWidth(item.label));
        }
        if (item.child?.length) {
          this.computedColumnsWidth(item.child, item);
        }
      });
    },
  },
};
</script>

<style lang="postcss" scoped>
  .process-attribute-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 450px;
    overflow: hidden;

    .page-head {
      padding-left: 20px;
      height: 50px;
      line-height: 49px;
      border-bottom: 1px solid #dcdee5;
      font-size: 16px;
      color: #313238;
      background: #fff;
    }

    .page-content {
      flex: 1;
      display: flex;
      background: #fff;
      overflow: hidden;
    }
  }

  .content-left {
    position: relative;
    width: 0;
    background: #f5f6fa;

    &.width-transition {
      transition: width .3s cubic-bezier(.4,0,.2,1);
    }

    .drag-box {
      position: absolute;
      top: 0;
      bottom: 0;
      right: -1px;
      width: 2px;
      border-left: 1px solid #dcdee5;
      z-index: 5;
      cursor: w-resize;

      &:hover {
        border-color: #3a84ff;
        z-index: 10;
      }
    }

    .drag-border {
      position: absolute;
      top: 0;
      height: 100%;
      padding: 0 2px;
      z-index: 5;
      cursor: w-resize;
    }

    .process-topo {
      width: 100%;
      height: 100%;
      overflow-x: hidden;
    }

    .process-topo-content {
      padding: 14px 0;
      min-width: 200px;
      height: 100%;
    }

    .topo-toggle {
      position: absolute;
      top: 40%;
      right: -20px;
      display: flex;
      align-items: center;
      width: 21px;
      height: 80px;
      border-radius: 0 6px 6px 0;
      color: #fff;
      background: #dcdee5;
      z-index: 5;
      cursor: pointer;

      &:hover {
        background: #a3c5fd;
      }

      .show-topo {
        transform: rotateY(180deg);
      }
    }
  }

  .content-right {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 16px 24px;
    overflow-x: hidden;
    overflow-y: auto;

    .topo-head {
      .topo-path {
        line-height: 16px;
        font-size: 12px;
        color: #979ba5;
      }

      .topo-name {
        margin: 0;
        line-height: 31px;
        font-size: 24px;
        font-weight: normal;
        color: #313238
      }
    }

    .temp-head {
      .title {
        display: flex;
        align-items: center;
        line-height: 32px;
        font-size: 24px;
      }

      .tag {
        display: inline-block;
        margin-right: 6px;
        padding: 0 4px;
        min-width: 40px;
        line-height: 20px;
        border-radius: 2px;
        text-align: center;
        font-size: 14px;
        color: #3a84ff;
        background: #e1ecff;
      }

      & + .temp-head {
        margin-top: 16px;
      }
    }

    .head-tips {
      display: flex;
      align-items: center;
      margin-top: 12px;
      padding: 0 8px;
      height: 32px;
      border: 1px solid #ffdfac;
      border-radius: 2px;
      background: #fff4e2;

      .tips-icon {
        font-size: 16px;
        color: #ffb848;
      }

      .tips-text {
        margin-left: 6px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 12px;
        color: #63656e;
      }
    }

    .content-operate {
      display: flex;
      justify-content: space-between;
      margin-top: 20px;

      .search-input {
        width: 520px;
      }
    }

    .content-table-block {
      flex: 1;
      margin-top: 16px;
    }
  }

  >>> .process-edit-slider .bk-sideslider-content {
    height: 100%;
  }

</style>
