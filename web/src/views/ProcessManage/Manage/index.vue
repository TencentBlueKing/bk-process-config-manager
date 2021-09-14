<template>
  <div class="process-manage">
    <div class="process-manage-header">{{ $t('进程管理') }}</div>
    <template v-if="isShowPageContent">
      <EmptyProcess v-if="isEmtpyTopo" empty-type="topo"></EmptyProcess>
      <div class="process-manage-body" v-else>
        <div class="manage-topology-tree">
          <div class="common-form-content">
            <div class="bk-button-group">
              <bk-button
                :theme="!isShowTopoTree ? 'primary' : 'default'"
                @click="onSwitchTaskType('service-template')">
                {{ $t('按服务模板') }}
              </bk-button>
              <bk-button
                :theme="!isShowTopoTree ? 'default' : 'primary'"
                @click="onSwitchTaskType('bussiness-topo')">
                {{ $t('按业务拓扑') }}
              </bk-button>
            </div>
          </div>
          <div class="common-form-content">
            <bk-input
              v-show="isShowTopoTree"
              v-model.trim="topoSearchKeyword"
              :placeholder="$t('请输入关键字')"
              :right-icon="'bk-icon icon-search'"
              clearable
              @change="handleSearch('topoData', $event)">
            </bk-input>
            <bk-input
              v-show="!isShowTopoTree"
              :placeholder="$t('请输入关键字')"
              :right-icon="'bk-icon icon-search'"
              v-model.trim="tempSearchKeyword"
              clearable
              @change="handleSearch('templateList', $event)">
            </bk-input>
          </div>
          <div v-show="isShowTopoTree" class="common-form-content tree-list" v-bkloading="{ isLoading, zIndex: 0 }">
            <TopoTree :node-list="topoData" node-reload @selected="handleSelected" />
          </div>
          <div v-show="!isShowTopoTree" class="common-form-content tree-list">
            <ServerTemplate :template-list="templateList" @templateInfo="onTemplateInfo" />
          </div>
        </div>
        <div class="manage-config-info">
          <EmptyServiceBox v-if="!isShowTopoTree && isEmtpyTemplate" type="template"></EmptyServiceBox>
          <EmptyServiceBox v-else-if="isShowTopoTree && isEmtpyInstance" type="instance" :info="emptyInstanceInfo" />
          <router-view
            v-else
            v-bkloading="{ isLoading: isDataLoading }"
            :table-data="tableData"
            :current-process="currentProcess"
            :process-info="processInfo"
            :process-instance="processInstance"
            :is-service-instance="isServiceInstance"
            :panels="panels"
            :process-id="processId"
            @handleDeleteProcess="handleDeleteProcess"
            @onCreateProcess="onCreateProcess"
            @onSaveEditor="onSaveEditor"
            @onBindConfigFile="onBindConfigFile"
            @onChangeTab="onChangeTab">
          </router-view>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import ServerTemplate from './ServerTemplate';
import TopoTree from './TopoTree';
import EmptyProcess from '@/components/Empty/EmptyProcess';
import EmptyServiceBox from '@/components/Empty/EmptyServiceBox';
import { sortByCustom } from '@/common/util';
export default {
  name: 'ProcessManage',
  components: {
    ServerTemplate,
    TopoTree,
    EmptyProcess,
    EmptyServiceBox,
  },
  data() {
    return {
      isDataLoading: false,
      isShowPageContent: false, // load 完成之后确定展示哪个页面
      isShowTopoTree: false,
      topoSearchKeyword: '',
      tempSearchKeyword: '',
      templateName: '',
      isServiceInstance: true,
      isLoading: false,
      topoData: [],
      searchTimer: null,
      templateList: [],
      isEmtpyTopo: false, // 展示空topo页
      isEmtpyTemplate: false, // 展示空模板页
      isEmtpyInstance: false, // 展示空实例页
      emptyInstanceInfo: {},
      currentProcess: {}, // 当前进程信息
      processInstance: [], // 调取接口获取的数据
      tableData: [],
      processInfo: {}, // 进程属性信息
      panels: [], // tab栏数据
      processNum: 0, // tab栏当前选中的下标
      serviceType: '', // 服务类型
      serviceId: null, // 服务id
      processId: null, // 接口获取的进程id
      topoInstId: null, // 拓扑节点的bk_inst_id
      isRouter: true,
    };
  },
  watch: {
    '$store.state.bizId'() {
      this.init();
    },
  },
  async created() {
    const { params } = this.$route;
    this.isServiceInstance = params.type === 'service-instance';
    await this.init();
    // 根据路由自动打开新建弹框
    const { serviceId, type } = this.$route.params;
    if (serviceId) {
      this.isRouter = true;
      this.serviceType = type;
      this.serviceId = serviceId;
      this.getProcessList(serviceId);
    }
  },
  methods: {
    // 设置拓扑选中状态
    setTopoActive(data) {
      data.forEach((item) => {
        const serviceId = item.service_template_id || item.service_instance_id || '';
        if (item.bk_inst_id) {
          item.topoActive = serviceId === this.serviceId && item.bk_inst_id === this.topoInstId;
        } else {
          item.topoActive = serviceId === this.serviceId;
        }
        if (item.child && item.child.length) {
          this.setTopoActive(item.child);
        }
      });
    },
    // 取消业务拓扑点击状态
    canCelTopoClickStatus(data) {
      data.forEach((item) => {
        item.topoActive = false;
        if (item.child && item.child.length) {
          this.canCelTopoClickStatus(item.child);
        }
      });
    },
    // 拓扑模块切换
    onSwitchTaskType(type) {
      this.isShowTopoTree = type === 'bussiness-topo';
    },
    async onTemplateInfo(val) {
      this.isRouter = false;
      this.isServiceInstance = false;
      this.templateName = val.name;
      this.serviceType = 'service-template';
      this.serviceId = val.id;
      await this.getProcessList(val.id);
      // 设置选中状态
      this.canCelTopoClickStatus(this.topoData);
      this.templateList.forEach((item) => {
        item.active = false;
      });
      val.active = true;
    },
    async handleSelected(val) {
      this.isRouter = false;
      if (val.topoType === 'module') {
        this.isEmtpyInstance = !val.child || !val.child.length;
        this.emptyInstanceInfo = val;
        if (this.isEmtpyInstance) {
          this.canCelTopoClickStatus(this.topoData);
          val.topoActive = true;
        }
      }
      // 提取服务实例 服务模板共同逻辑
      this.setPublicCode(val);
      if (val.topoType === 'serviceInstance') {
        this.serviceType = 'service-instance';
        await this.getProcessList(val.service_instance_id);
      } else if (val.topoType === 'serviceTemplate') {
        this.templateName = val.bk_inst_name;
        this.serviceType = 'service-template';
        await this.getProcessList(val.service_template_id);
      }
    },
    // 提取服务实例 服务模板共同逻辑
    setPublicCode(val) {
      const type = ['serviceInstance', 'serviceTemplate'];
      if (type.includes(val.topoType)) {
        this.topoInstId = val.bk_inst_id;
        this.isEmtpyInstance = false;
        if (val.topoType === 'serviceInstance') {
          this.serviceId = val.service_instance_id;
        } else {
          this.serviceId = val.service_template_id;
        }
        this.isServiceInstance = val.topoType === 'serviceInstance';
        // 设置选中状态
        this.setTopoActive(this.topoData);
        this.templateList.forEach((item) => {
          item.active = false;
        });
      }
    },
    // 获取topo树和服务模板列表，接口获取的服务模板列表数据不同于topo树里面的服务模板
    async init() {
      this.isShowPageContent = false;
      try {
        this.isLoading = true;
        const [topoRes, templateRes] = await Promise.all([
          this.$store.dispatch('cmdb/ajaxGetBizTopo'),
          this.$store.dispatch('cmdb/ajaxGetServiceTemplate'),
        ]);
        templateRes.data.forEach((item) => {
          item.active = false;
          item.visible = true;
        });
        templateRes.data.sort(sortByCustom('name'));
        this.templateList = templateRes.data;
        if (topoRes.data && topoRes.data.length) {
          const topoData = topoRes.data[0].child;
          this.filterTopoData(topoData);
          this.topoData = topoData;
          this.isEmtpyTopo = !topoData.length;
        } else {
          this.isEmtpyTopo = true;
        }
        this.isEmtpyTemplate = !templateRes.data || !templateRes.data.length;
      } catch (e) {
        console.warn(e);
      } finally {
        this.isShowPageContent = true;
        this.isLoading = false;
      }
    },
    filterTopoData(topoData, topoLevel = -1, parent = null) {
      topoLevel += 1;
      topoData.sort(sortByCustom('bk_inst_name'));
      topoData.forEach((item) => {
        item.topoParent = parent;
        item.topoVisible = true;
        item.topoExpand = false;
        item.topoLoading = false;
        item.topoloaded = true;
        item.topoActive = false;
        item.topoLevel = topoLevel;
        item.topoName = item.bk_inst_name;
        item.topoReduceName = parent ? parent.topoReduceName + item.topoName : item.topoName;
        if (item.bk_obj_id === 'set') {
          item.topoType = 'set'; // 集群
        } else if (item.bk_obj_id === 'module') {
          item.empty = true;
          item.topoloaded = false;
          if (item.service_template_id) { // 服务模板
            item.topoType = 'serviceTemplate';
          } else { // 模块
            item.topoType = 'module';
          }
        }
        if (item.child && item.child.length) {
          this.filterTopoData(item.child, topoLevel, item);
        }
      });
    },
    handleSearch(treeData, keyword) {
      this.isLoading = true;
      this.searchTimer && clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => {
        const list = this[treeData];
        if (treeData === 'topoData') {
          this.searchTree(list, keyword);
        } else {
          this.searchTemplate(list, keyword);
        }
        this.isLoading = false;
      }, 300);
    },
    searchTemplate(list, keyword) {
      list.forEach((item) => {
        const isMatched = item.name.includes(keyword);
        item.visible = isMatched;
      });
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
    // 获取服务实例进程实例列表
    async getProcessList(serviceId) {
      this.isDataLoading = true;
      try {
        let res;
        if (this.isServiceInstance) {
          res = await this.$store.dispatch('process/ajaxGetInstanceProcessByServiceInstance', {
            serviceInstanceId: serviceId,
          });
        } else {
          res = await this.$store.dispatch('process/ajaxGetTemplateProcessByServiceTemplate', {
            serviceTemplateId: serviceId,
          });
        }
        if (!res.data.length) {
          this.processInstance = res.data;
          // 如果没有进程 processInfo将数据清空
          const processInfo = {};
          for (const key of Object.keys(this.processInfo)) {
            if (key !== 'auto_start') {
              processInfo[key] = key === 'bind_info' ? [] : '';
            }
          }
          this.processInfo = processInfo;
          this.processId = null;
          // 如果刷新的话 就不进行路由跳转
          if (this.isRouter) return;
          this.handleRouter();
          return;
        }
        // 进程信息必填项
        const mandatory = ['work_path', 'user', 'pid_file', 'start_cmd', 'stop_cmd'];
        res.data.forEach((item) => {
          let isFull = true;
          for (const [key, value] of Object.entries(item.property)) {
            if (mandatory.includes(key)) {
              if (!value) {
                isFull = false;
              }
            }
          }
          this.$set(item, 'is_full', isFull);
        });
        // tab栏数据处理
        this.panels = res.data.length && res.data.map(item => ({
          label: item.property.bk_process_name,
          name: item.property.bk_process_name,
          id: this.isServiceInstance ? item.property.bk_process_id : item.id,
          isFull: item.is_full,
          count: item.config_templates.length,
        }));
        this.processInstance = res.data;
        // 如果有processId 就获取位于tab栏的第几个
        const { processId } = this.$route.params;
        if (processId) {
          const index = res.data.findIndex((item) => {
            const id = this.isServiceInstance ? item.property.bk_process_id : item.id;
            return Number(processId) === id;
          });
          this.processNum = index > -1 ? index : 0;
        }
        const currentProcess = this.processInstance[this.processNum];
        this.currentProcess = currentProcess;
        this.processInfo = currentProcess.property;
        this.tableData = currentProcess.config_templates;
        this.processId = this.panels[this.processNum].id;
        // 如果刷新的话 就不进行路由跳转
        if (this.isRouter) return;
        this.handleRouter();
      } catch (error) {
        console.warn(error);
        this.isDataLoading = false;
      } finally {
        this.isDataLoading = false;
      }
    },
    handleRouter() {
      this.$store.commit('routeProcessManageConfigInformationInstance', {
        type: this.serviceType,
        serviceId: this.serviceId,
        processId: this.processId,
      });
    },
    // tab栏切换
    async onChangeTab(id) {
      const processId = Number(id);
      const index = this.processInstance.findIndex((item) => {
        const id = this.isServiceInstance ? item.property.bk_process_id : item.id;
        return Number(processId) === id;
      });
      this.processNum = index > -1 ? index : 0;
      const currentProcess = this.processInstance[this.processNum];
      this.currentProcess = currentProcess;
      this.processInfo = currentProcess.property;
      this.tableData = currentProcess.config_templates;
      this.processId = processId;
      this.handleRouter();
    },
    // 绑定文件
    onBindConfigFile() {
      this.isRouter = true;
      this.getProcessList(this.serviceId);
    },
    // 编辑属性
    onSaveEditor() {
      this.isRouter = true;
      this.getProcessList(this.serviceId);
    },
    // 创建进程or创建进程模板
    onCreateProcess() {
      this.isRouter = true;
      this.getProcessList(this.serviceId);
    },
    // 删除进程
    handleDeleteProcess(isRouter) {
      this.isRouter = isRouter;
      this.getProcessList(this.serviceId);
    },
  },
};
</script>

<style lang="postcss" scoped>
  @import '../../../css/mixins/scroll.css';

  .process-manage {
    display: flex;
    flex-direction: column;
    width: 100%;
    height: 100%;
    background-color: #f5f6fa;

    .process-manage-header {
      height: 56px;
      padding: 18px 22px 16px;
      border-bottom: 1px solid #dcdee5;
      font-size: 16px;
      color: #313238;
    }

    .process-manage-body {
      height: calc(100% - 56px);
      display: flex;

      .manage-topology-tree {
        width: 320px;
        padding: 16px 0;
        background: #f5f6fa;
        border-right: 1px solid #dcdee5;

        .common-form-content {
          padding: 0 16px;
          display: flex;
          margin-bottom: 12px;

          .bk-button-group {
            .bk-button {
              width: 143px;
              margin: 0px;
            }

            .bk-button.bk-primary {
              position: relative;
              z-index: 4;
              color: #3a84ff;
              background-color: #c7dcff;
              border-radius: 2px;
              border: 1px solid #3a84ff;
            }

            .bk-button:last-child {
              margin-left: -1px;
            }
          }
        }

        .tree-list {
          padding: 0;
          margin-bottom: 0;
          height: calc(100% - 88px);
          overflow: auto;

          @mixin scroller;
        }
      }

      .manage-config-info {
        width: calc(100% - 320px);
      }
    }
  }
</style>
