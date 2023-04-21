<template>
  <div class="instance-table-container">
    <div class="header">
      <div class="header-left">
        <div class="bk-icon icon-down-shape" :class="!showTable && 'close'" @click="showTable = !showTable"></div>
        <div class="config-name">{{ configTemplate.template_name + ' / ' + configTemplate.file_name }}</div>
        <i18n
          class="version-to-dis"
          v-if="versionList.length"
          tag="div"
          :path="isConfigCheck ? '最后一次下发版本' : '即将下发版本'">
          <span class="blue" v-bk-tooltips="activeTippy">#{{ activeVersion.config_version_id }}</span>
        </i18n>
      </div>
      <div v-if="curStep === 1" class="header-right-1">
        <!-- eslint-disable-next-line vue/no-v-html -->
        <span v-if="isConfigCheck" v-html="$t('已选x个', { x: totalCount })"></span>
        <template v-else-if="selectedVersionIds.length">
          <div class="version-selector selected" @click="toggleVersionList">
            <div class="gsekit-icon gsekit-icon-filter-fill blue"></div>
            {{ $t('已选x个版本', { x: `${selectedVersionIds.length}/${usedVersionList.length}` }) }}
          </div>
          <span class="split-line"></span>
          <!-- eslint-disable-next-line vue/no-v-html -->
          <span v-html="$t('已选x个', { x: totalCount })"></span>
        </template>
        <template v-else>
          <template v-if="usedVersionList.length">
            <div class="version-selector" v-bk-tooltips="$t('高级选项，可按版本进一步过滤下发对象')" @click="toggleVersionList">
              <span class="gsekit-icon gsekit-icon-filter-fill"></span>
              {{ $t('按版本选择') }}
            </div>
            <span class="split-line"></span>
          </template>
          <!-- eslint-disable-next-line vue/no-v-html -->
          <span v-html="$t('共x个', { x: totalCount })"></span>
        </template>
      </div>
      <div v-if="curStep === 2" class="header-right-2">
        <div class="statue-counter-tips" v-show="statusCounter.succeeded">
          <span class="num success">{{ statusCounter.succeeded }}</span>
          {{ $t('已生成') }}
        </div>
        <div class="statue-counter-tips" v-show="statusCounter.failed">
          <span class="num failed">{{ statusCounter.failed }}</span>
          {{ $t('生成失败') }}
        </div>
        <div class="statue-counter-tips" v-show="statusCounter.pending + statusCounter.running">
          <span class="num loading">{{ statusCounter.pending + statusCounter.running }}</span>
          {{ $t('生成中') }}
        </div>
      </div>
    </div>
    <div class="version-list" v-show="curStep === 1 && showTable && showVersionList && usedVersionList.length">
      <bk-checkbox-group class="king-checkbox-group" :value="selectedVersionIds" @change="handleVersionsChange">
        <template v-for="item in usedVersionList">
          <bk-checkbox class="king-checkbox" :key="item.config_version_id" :value="item.config_version_id">
            <div v-bk-tooltips="getVersionTippy(item)">
              #{{ item.config_version_id }} {{ item.description }}
              <span class="percent">({{ $t('占比x%', { x: versionPercents[item.config_version_id] }) }})</span>
            </div>
          </bk-checkbox>
        </template>
      </bk-checkbox-group>
    </div>
    <bk-table
      class="king-table"
      :max-height="maxHeight"
      :data="tableLoadedList"
      :empty-text="$t('当前指定范围未能匹配到实例，请确认所选范围是否有误，或对应范围是否存在主机')"
      v-show="showTable"
      v-bkloading="{ isLoading: tableLoading, zIndex: 0 }">
      <bk-table-column :label="$t('进程别名')" min-width="140">
        <div v-bk-overflow-tips class="table-ceil-overflow" slot-scope="{ row }">
          <span>{{ row.bk_process_name }}</span>
        </div>
      </bk-table-column>
      <bk-table-column :label="$t('所属拓扑')" min-width="400">
        <div v-bk-overflow-tips class="table-ceil-overflow" slot-scope="{ row }">
          <span>{{ row.bk_set_name }} / {{ row.bk_module_name }} / {{ row.bk_service_name }}</span>
        </div>
      </bk-table-column>
      <bk-table-column label="process_id" min-width="140">
        <div v-bk-overflow-tips class="table-ceil-overflow" slot-scope="{ row }">
          <span>{{ row.bk_process_id }}</span>
        </div>
      </bk-table-column>
      <bk-table-column label="inst_id" min-width="110">
        <div v-bk-overflow-tips class="table-ceil-overflow" slot-scope="{ row }">
          <span>{{ row.inst_id }}</span>
        </div>
      </bk-table-column>
      <template v-if="curStep === 1">
        <bk-table-column :label="$t('版本号')" min-width="140" key="configVersionId">
          <div v-bk-overflow-tips class="table-ceil-overflow" slot-scope="{ row }">
            <span>#{{ row.config_version_id }}</span>
          </div>
        </bk-table-column>
        <bk-table-column :label="$t('版本描述')" min-width="140" key="configVersionDescription">
          <div v-bk-overflow-tips class="table-ceil-overflow" slot-scope="{ row }">
            <span>{{ row.configVersionDescription }}</span>
          </div>
        </bk-table-column>
        <bk-table-column :label="$t('操作')" min-width="140" key="compareConfiguration">
          <template slot-scope="{ row }">
            <bk-popover
              v-if="isConfigCheck"
              :disabled="row.status === 'generated' && row.config_instance_id"
              :content="row.status === 'not_generated' ? $t('未生成配置，请先生成并下发配置再进行配置检查 ') : $t('请先下发配置再进行配置检查')">
              <bk-button
                theme="primary"
                text
                :disabled="row.status === 'not_generated' || !row.config_instance_id"
                @click="handleViewConfig(row)">
                {{ $t('查看配置') }}
              </bk-button>
            </bk-popover>
            <bk-button v-else theme="primary" text @click="compareConfiguration(row)">
              {{ $t('配置对比') }}
            </bk-button>
          </template>
        </bk-table-column>
      </template>
      <template v-if="curStep === 2">
        <bk-table-column :label="$t('状态')" prop="taskStatus" min-width="110" key="taskStatus">
          <div slot-scope="{ row }">
            <StatusView
              v-if="row.taskStatus === 'pending' || row.taskStatus === 'running'"
              type="loading"
              :text="$t('生成中')" />
            <StatusView v-if="row.taskStatus === 'succeeded'" type="success" :text="$t('已生成')" />
            <GenerateFailed
              v-else-if="row.taskStatus === 'failed'"
              :failed-reason="row.failed_reason"
              :solutions="row.solutions" />
          </div>
        </bk-table-column>
        <bk-table-column :label="$t('生成时间')" min-width="170" key="generatedTime">
          <div v-bk-overflow-tips class="table-ceil-overflow" slot-scope="{ row }">
            <span>{{ row.generatedTime || '--' }}</span>
          </div>
        </bk-table-column>
        <bk-table-column :label="$t('操作')" min-width="140" key="regenerate">
          <template slot-scope="{ row }">
            <bk-button
              theme="primary" text style="margin-right: 6px;"
              v-test.release="'generate'"
              :disabled="isTasking || row.taskStatus === 'pending' || row.taskStatus === 'running'"
              @click="regenerate(row)">
              {{ $t('重新生成') }}
            </bk-button>
            <bk-popover :disabled="!!row.config_instance_id" :content="$t('没有绑定配置实例，暂无法查看')">
              <bk-button
                theme="primary"
                text
                style="margin-right: 6px;"
                :disabled="!row.config_instance_id || row.taskStatus === 'pending' || row.taskStatus === 'running'"
                @click="handleViewConfig(row)">
                {{ $t('查看') }}
              </bk-button>
            </bk-popover>
          </template>
        </bk-table-column>
      </template>
    </bk-table>
    <!-- 配置对比 -->
    <bk-sideslider
      :is-show.sync="sliderData.isShow"
      :quick-close="true"
      :width="1200"
      @hidden="handleCloseSlider">
      <div class="config-contrast-header" slot="header">
        <span>{{ $t('配置对比') }}</span>
        <span class="divide-line">{{ '-' }}</span>
        <span class="template-name">{{ configTemplate.template_name + '(' + configTemplate.file_name + ')' }}</span>
      </div>
      <div v-bkloading="{ isLoading: sliderData.isLoading }" style="height: calc(100vh - 60px);" slot="content">
        <SidesliderDiff v-if="sliderData.oldData" :old-data="sliderData.oldData" :new-data="sliderData.newData">
          <template slot="leftTitle">
            <div class="status-flag">{{ $t('实时') }}</div>
            <div class="create-time">{{ $t('更新时间') + $t('：') + (formatDate(sliderData.oldData.time) || '--') }}</div>
          </template>
          <template slot="rightTitle">
            <div class="status-flag">{{ $t('预生成') }}</div>
            <div class="create-time">{{ $t('生成时间') + $t('：') + (formatDate(sliderData.newData.time) || '--') }}</div>
          </template>
        </SidesliderDiff>
      </div>
    </bk-sideslider>
    <!-- 查看配置 -->
    <ViewConfig :instances-config="viewConfigData" @onCloseSide="viewConfigData = null"></ViewConfig>
  </div>
</template>

<script>
import { formatDate } from '@/common/util';
import SidesliderDiff from '@/components/SidesliderDiff';
import ViewConfig from '@/components/ViewConfig';
import GenerateFailed from '@/components/GenerateFailed';

export default {
  components: {
    SidesliderDiff,
    ViewConfig,
    GenerateFailed,
  },
  props: {
    action: {
      type: String,
      default: '',
    },
    curStep: {
      type: Number,
      default: 1,
    },
    originList: {
      type: Array,
      required: true,
    },
    isTasking: {
      type: Boolean,
      required: true,
    },
    isDropdownMode: {
      type: Boolean,
      required: true,
    },
    selectedScope: {
      type: Object,
      required: true,
    },
    configTemplate: {
      type: Object,
      required: true,
    },
    maxHeight: {
      type: Number,
      default: 464,
    },
  },
  data() {
    return {
      versionList: [], // 版本列表
      versionPercents: [], // 版本占比统计
      versionInfoMap: [], // 版本 id: description 映射表
      selectedVersionIds: [], // 选择的版本 id
      completeInstanceList: [], // 总的实例列表，包含所有版本
      filterInstanceList: [], // 根据选择的版本筛选后的实例列表，第二步就不会再变了

      isThrottled: false, // 滚动节流 是否进入cd
      isPageOver: false, // 前端分页加载是否结束
      tableScroller: null, // 滚动容器
      tableLoadedList: [], // 展示的列表数据
      tablePagedList: [], // 将按版本过滤的列表数据按 pageSize 分页
      pageSize: 15, // 每页展示多少数据
      totalCount: 0, // 数据总条数
      totalPage: 0, // 计算出总共多少页
      currentPage: 0, // 当前加载了多少页

      tableLoading: true,
      showTable: true,
      showVersionList: false,

      formatDate,
      sliderData: {
        isShow: false,
        isLoading: false,
        oldData: null, // 配置对比数据
        newData: null, // 配置对比数据
      },
      viewConfigData: null,

      jobTimer: null, // 配置生成之后查看 job 状态
      taskTimer: null, // job 状态完成之后查看 task 状态
      jobId: null, // 配置生成任务 id
      isJobReady: false, // 为 true 时，分页加载才可请求 task list 更新配置生成任务状态
      hasPollingTask: false, // 是否有配置生成轮询任务
      statusCounter: {
        succeeded: 0,
        failed: 0,
        pending: 0,
        running: 0,
      },
      scrollLoading: false, // 必须加载完成之后再加载。否则会导致取消请求而不能执行下一步
      needPromissRes: false, // 是否需要 generateConfig generateFailure 执行的结果
      tableResolve: null,
    };
  },
  computed: {
    templateId() {
      return Number(this.configTemplate.config_template_id);
    },
    isConfigCheck() {
      return this.action === 'configCheck';
    },
    // 版本有在使用的版本列表
    usedVersionList() {
      return this.versionList.filter(item => this.versionPercents[item.config_version_id] !== undefined);
    },
    activeVersion() {
      let activeVersion = this.versionList.find(item => item.is_active);
      if (!activeVersion) {
        console.error('无可用版本');
        activeVersion = {};
      }
      return activeVersion;
    },
    activeTippy() {
      if (!this.activeVersion) {
        return {
          disabled: true,
        };
      }
      const updateBy = this.$t('更新人') + this.$t('：') + this.activeVersion.updated_by;
      const updateAt = this.$t('更新时间') + this.$t('：') + formatDate(this.activeVersion.updated_at);
      return {
        placement: 'right',
        content: `${updateBy}<br>${updateAt}`,
      };
    },
  },
  created() {
    this.init();
  },
  mounted() {
    this.tableScroller = this.$el.querySelector('.bk-table-body-wrapper');
    this.tableScroller.addEventListener('scroll', this.handleTableScroll, { passive: true });
  },
  beforeDestroy() {
    this.tableScroller.removeEventListener('scroll', this.handleTableScroll);
    this.jobTimer && clearTimeout(this.jobTimer);
    this.taskTimer && clearTimeout(this.taskTimer);
  },
  methods: {
    async init() {
      try {
        const versionRes = await this.$store.dispatch('configTemplate/ajaxGetConfigVersionList', {
          templateId: this.templateId,
        });
        const versionInfoMap = {};
        versionRes.data.forEach((item) => {
          versionInfoMap[item.config_version_id] = item;
        });
        versionRes.data.push({
          config_version_id: '-',
          description: this.$t('未下发'),
        });
        this.versionList = versionRes.data;
        this.versionInfoMap = versionInfoMap;
        this.initTableData();
      } catch (e) {
        console.warn(e);
      } finally {
        this.tableLoading = false;
      }
    },

    // 暴露给父组件的方法，下一步 - 重置表格数据
    initTableData() {
      const versionCounter = {};
      const versionPercents = {};
      const instanceList = JSON.parse(JSON.stringify(this.originList));
      const instanceLength = instanceList.length;
      instanceList.forEach((item) => {
        item.taskStatus = '';
        item.generatedTime = formatDate(item.created_at);
        // 实例已下发的版本
        const versionId = item.config_version_id;
        if (versionId === '-') {
          // 还未根据配置版本生成实例
          item.configVersionDescription = '--';
        } else {
          item.configVersionDescription = this.versionInfoMap[versionId].description;
        }
        if (versionCounter[versionId]) {
          versionCounter[versionId] += 1;
        } else {
          versionCounter[versionId] = 1;
        }
      });
      for (const [key, value] of Object.entries(versionCounter)) {
        versionPercents[key] = Math.round(value / instanceLength * 100);
      }
      Object.assign(this, {
        versionPercents,
        completeInstanceList: instanceList,
        filterInstanceList: instanceList,
      });
      this.initPagination();
    },
    // 根据按版本过滤后的实例列表分页
    initPagination() {
      const list = this.filterInstanceList;
      if (!list.length) {
        this.tableLoadedList.splice(0);
        this.tablePagedList.splice(0);
        this.isPageOver = true;
        this.totalCount = 0;
        this.totalPage = 0;
        this.currentPage = 0;
        return;
      }
      this.isPageOver = false;
      this.totalCount = list.length;
      this.totalPage = Math.ceil(this.totalCount / this.pageSize);
      this.currentPage = 0;
      this.tableLoadedList.splice(0);
      this.tablePagedList.splice(0);
      for (let i = 0; i < this.totalCount; i += this.pageSize) {
        this.tablePagedList.push(list.slice(i, i + this.pageSize));
      }
      this.loadPage();
      this.tableScroller.scrollTop = 0;
    },
    loadPage() {
      if (!this.scrollLoading) {
        this.currentPage += 1;
        this.isPageOver = this.currentPage === this.totalPage;
        this.tableLoadedList.splice(this.tableLoadedList.length, 0, ...this.tablePagedList[this.currentPage - 1]);
        this.handlePageAdd();
      }
    },
    handleTableScroll() {
      if (!this.isPageOver && !this.isThrottled) {
        this.isThrottled = true;
        setTimeout(() => {
          this.isThrottled = false;
          const el = this.tableScroller;
          if (el.scrollHeight - el.offsetHeight - el.scrollTop < 10) {
            this.loadPage();
          }
        }, 200);
      }
    },

    // 按版本选择
    toggleVersionList() {
      this.showVersionList = !this.showVersionList;
    },
    // 选择指定版本
    async handleVersionsChange(val) {
      this.selectedVersionIds = val;
      if (val.length) {
        this.filterInstanceList = [];
        const newList = await this.getInstanceListByVersions();
        // 如果在请求的时候又选择了版本，会取消上次请求并重新请求
        if (newList) {
          this.filterInstanceList = newList;
        }
      } else {
        this.filterInstanceList = this.completeInstanceList;
      }
      this.initPagination();
      this.$emit('update-version', { [this.templateId]: val });
    },
    // 根据指定版本重新请求实例列表（为了保证 task list 能和实例列表顺序保持一致）
    async getInstanceListByVersions() {
      try {
        this.tableLoading = true;
        const res = await this.$store.dispatch('configInstance/ajaxGetConfigInstanceList', {
          data: {
            [this.isDropdownMode ? 'scope' : 'expression_scope']: this.selectedScope,
            config_template_id: this.templateId,
            config_version_ids: this.selectedVersionIds,
            filter_released: true, // 实例的item.config_version_id版本显示的是下发的版本，而不是生成的版本
          },
        });
        res.data.forEach((item) => {
          item.taskStatus = '';
          item.generatedTime = formatDate(item.created_at);
          if (item.config_version_id === '-') {
            item.configVersionDescription = '--';
          } else {
            item.configVersionDescription = this.versionInfoMap[item.config_version_id].description;
          }
        });
        return res.data;
      } catch (e) {
        console.warn(e);
        return null;
      } finally {
        this.tableLoading = false;
      }
    },

    // 暴露给父组件的方法，配置生成
    async generateConfig({ isFirstStep }) {
      return new Promise(async (resolve) => {
        if (isFirstStep && this.filterInstanceList.every(item => item.status === 'generated')) {
          // 配置下发第一步下一步，如果已经生成配置就不重新生成了
          this.filterInstanceList.forEach((item) => {
            item.taskStatus = 'succeeded';
          });
          this.statusCounter.succeeded = this.filterInstanceList.length;
          resolve(true);
        } else {
          try {
            this.needPromissRes = true;
            this.tableResolve = resolve;

            this.jobId = null;
            this.isJobReady = false;
            this.hasPollingTask = false;
            this.filterInstanceList.forEach((item) => {
              item.taskStatus = 'running';
            });
            this.statusCounter = {
              succeeded: 0, // 已生成
              failed: 0, // 生成失败
              pending: 0, // 生成中
              running: this.filterInstanceList.length, // 生成中
            };
            const res = await this.$store.dispatch('configTemplate/ajaxGenerateConfig', {
              data: {
                config_template_id: this.templateId,
                [this.isDropdownMode ? 'scope' : 'expression_scope']: this.selectedScope,
                config_version_ids: this.selectedVersionIds,
              },
            });
            this.jobId = res.data.job_id;
            this.hasPollingTask = true;
            this.pollingJobStatus(resolve);
          } catch (e) {
            console.warn(e);
            resolve(false);
            this.needPromissRes = false;
          }
        }
      });
    },
    // job 状态轮询，job 执行成功后再轮询 task
    pollingJobStatus(resolve) {
      this.jobTimer = setTimeout(async () => {
        try {
          const res = await this.$store.dispatch('job/ajaxGetJobDetail', {
            jobId: this.jobId,
          });
          if (res.data.is_ready) {
            if (res.data.status === 'failed') {
              this.jobId = null;
              this.hasPollingTask = false;
              const reason = res.data.extra_data.failed_reason;
              this.filterInstanceList.forEach((item) => {
                item.taskStatus = 'failed';
                item.failed_reason = reason;
              });
              this.statusCounter = {
                succeeded: 0, // 已生成
                failed: this.filterInstanceList.length, // 生成失败
                pending: 0, // 生成中
                running: 0, // 生成中
              };
              resolve(false);
              this.needPromissRes = false;
            } else {
              this.isJobReady = true;
              this.getTaskList(resolve);
            }
          } else {
            this.pollingJobStatus(resolve);
          }
        } catch (e) {
          console.warn(e);
          this.pollingJobStatus(resolve);
        }
      }, 2000);
    },
    // job 创建成功后拉取 task 列表
    async getTaskList(resolve) {
      try {
        this.scrollLoading = true;
        // 滚动加载分页状态时清除之前的状态轮询，新的 task list 开启新一轮轮询
        this.taskTimer && clearTimeout(this.taskTimer);
        const res = await this.$store.dispatch('job/ajaxGetJobTaskList', {
          jobId: this.jobId,
          data: {
            page: 1,
            pagesize: this.tableLoadedList.length,
          },
        });
        if (this.hasPollingTask) {
          this.statusCounter = res.data.status_counter;
        } else {
          // 当轮询结束后，部分成功部分失败，可以点击单个进程重新生成，
          // 这个时候滚动分页请求 taskList 只需要更新可见列表状态
        }
        const pollingTaskList = [];
        this.tableLoadedList.forEach((instanceItem, instanceIndex) => {
          // 从 task list 里面找到对应实例的任务，后台保证顺序一致
          // const matchTaskItem = res.data.find(taskItem => {
          //     return taskItem.bk_process_id === instanceItem.bk_process_id
          //         && taskItem.extra_data.inst_id === instanceItem.inst_id
          // })
          const matchTaskItem = res.data.list[instanceIndex];

          instanceItem.generatedTime = formatDate(matchTaskItem.start_time);
          // 更新配置实例 id
          try {
            const configInstances = matchTaskItem.extra_data.config_instances;
            if (configInstances.length) {
              instanceItem.config_instance_id = configInstances
                .find(item => item.config_template_id === this.templateId).id;
            } else {
              // 没有绑定配置实例
            }
          } catch (e) {
            console.warn('任务列表返回数据格式错误，没有找到新的配置实例ID');
            console.warn(e);
          }

          const { id: taskId, status: taskStatus } = matchTaskItem;
          if (taskStatus === 'succeeded') {
            instanceItem.taskStatus = 'succeeded';
          } else if (taskStatus === 'failed') {
            instanceItem.taskStatus = 'failed';
            instanceItem.failed_reason = matchTaskItem.extra_data.failed_reason;
            instanceItem.solutions = matchTaskItem.extra_data.solutions;
          } else {
            pollingTaskList.push({ taskId, instanceIndex });
          }
        });
        if (this.hasPollingTask) {
          if (this.judgeTaskDone()) {
            this.hasPollingTask = false;
            resolve(this.statusCounter.failed === 0);
            this.needPromissRes = false;
          } else { // judgeTaskDone 返回 false 有可能是生成完成之后同步生成造成的
            this.pollingTaskStatus(pollingTaskList, resolve);
          }
        } else {
          // 当轮询结束后，部分成功部分失败，可以点击单个进程重新生成，
          // 这个时候滚动分页请求 taskList 只需要更新可见列表状态
        }
      } catch (e) {
        console.warn(e);
        resolve(false);
        this.needPromissRes = false;
      } finally {
        this.scrollLoading = false;
      }
    },
    // task 轮询
    pollingTaskStatus(pollingTaskList, resolve) {
      this.taskTimer = setTimeout(async () => {
        try {
          const res = await this.$store.dispatch('job/ajaxGetJobStatus', {
            jobId: this.jobId,
            data: {
              job_task_id_list: pollingTaskList.map(item => item.taskId),
            },
          });
          this.statusCounter = res.data.status_counter;
          const newPollingTaskList = [];
          // 这里接口应保证顺序和请求的 id 顺序一致
          pollingTaskList.forEach((pollingTask, pollingIndex) => {
            const instanceItem = this.filterInstanceList[pollingTask.instanceIndex];
            const pollingTaskItem = res.data.job_tasks[pollingIndex];
            const newTaskStatus = pollingTaskItem.status;
            if (newTaskStatus === 'succeeded') {
              instanceItem.taskStatus = 'succeeded';
            } else if (newTaskStatus === 'failed') {
              instanceItem.taskStatus = 'failed';
              instanceItem.failed_reason = pollingTaskItem.extra_data.failed_reason;
              instanceItem.solutions = pollingTaskItem.extra_data.solutions;
            } else {
              newPollingTaskList.push(pollingTask);
            }
          });
          if (this.judgeTaskDone()) {
            this.hasPollingTask = false;
            resolve(this.statusCounter.failed === 0);
            this.needPromissRes = false;
          } else {
            this.pollingTaskStatus(newPollingTaskList, resolve);
          }
        } catch (e) {
          console.warn(e);
          this.pollingTaskStatus(pollingTaskList, resolve);
        }
      }, 5000);
    },
    // 根据 statusCounter 是否有进行中的任务判断 task 是否结束
    judgeTaskDone() {
      return (this.statusCounter.pending + this.statusCounter.running) === 0;
    },
    handlePageAdd() {
      if (this.jobId !== null && this.isJobReady) {
        // 需要更新 task_list 获取配置生成后的状态
        this.getTaskList(this.needPromissRes ? this.tableResolve : null);
      }
    },

    // 暴露给父组件的方法，重试所有失败
    generateFailure() {
      return new Promise(async (resolve) => {
        if (!this.jobId || !this.statusCounter.failed) {
          // 没有失败任务需要重试
          resolve(true);
          return;
        }
        try {
          this.needPromissRes = true;
          this.tableResolve = resolve;
          // 重试时把表格设为加载状态禁止操作表格，等重试完成，再请求 task list 获取最新状态
          this.tableLoading = true;
          this.hasPollingTask = true;
          await this.$store.dispatch('job/ajaxRetryJob', {
            jobId: this.jobId,
          });
          this.tableLoadedList.forEach((item) => {
            if (item.taskStatus === 'failed') {
              item.taskStatus = 'running';
            }
          });
          this.tableLoading = false;
          this.getTaskList(resolve);
        } catch (e) {
          console.warn(e);
          this.tableLoading = false;
          this.hasPollingTask = false;
          resolve(false);
          this.needPromissRes = false;
        }
      });
    },

    // 暴露给父组件的方法，配置下发
    distributeConfig() {
      return new Promise(async (resolve) => {
        try {
          const actionMethod = `configTemplate/${this.isConfigCheck ? 'ajaxSetDiffConfig' : 'ajaxSetReleaseConfig'}`;
          const data = {
            config_template_id: this.templateId,
            [this.isDropdownMode ? 'scope' : 'expression_scope']: this.selectedScope,
          };
          if (!this.isConfigCheck) {
            data.config_version_ids = this.selectedVersionIds;
          }
          const res = await this.$store.dispatch(actionMethod, { data });
          resolve({ jobId: res.data.job_id });
        } catch (e) {
          console.warn(e);
          resolve({ jobId: null });
        }
      });
    },

    // 同步重新生成某个进程 id 相关的实例
    async regenerate(row) {
      // 同步生成单个进程下的实例时，其他操作都会被禁用
      this.$emit('update:isTasking', true);
      const generateList = this.filterInstanceList.filter(item => item.bk_process_id === row.bk_process_id);
      generateList.forEach((item) => {
        if (item.taskStatus === 'succeeded') {
          this.statusCounter.succeeded -= 1;
        } else if (item.taskStatus === 'failed') {
          this.statusCounter.failed -= 1;
        }
        item.taskStatus = 'running';
        this.statusCounter.running += 1;
      });
      try {
        const res = await this.$store.dispatch('configTemplate/ajaxSyncGenerateConfig', {
          data: {
            bk_process_id: row.bk_process_id,
          },
          templateId: this.templateId,
        });
        generateList.forEach((item) => {
          const matchTaskItem = res.data.find(taskItem => item.inst_id === taskItem.extra_data.inst_id) || {};
          if (matchTaskItem.status === 'succeeded') {
            item.taskStatus = 'succeeded';
            this.statusCounter.running -= 1;
            this.statusCounter.succeeded += 1;
          } else if (matchTaskItem.status === 'failed') {
            item.taskStatus = 'failed';
            item.failed_reason = matchTaskItem.extra_data.failed_reason;
            item.solutions = matchTaskItem.extra_data.solutions;
            this.statusCounter.running -= 1;
            this.statusCounter.failed += 1;
          } else {
            console.warn('同步生成接口出错，没有 matchTaskItem 或者状态不对');
            item.taskStatus = 'failed';
            this.statusCounter.running -= 1;
            this.statusCounter.failed += 1;
          }
          item.generatedTime = formatDate(matchTaskItem.start_time);
          // 更新配置实例 id
          try {
            const configInstances = matchTaskItem.extra_data.config_instances;
            if (configInstances.length) {
              item.config_instance_id = configInstances.find(ins => ins.config_template_id === this.templateId).id;
            } else {
              // 没有绑定配置实例
            }
          } catch (e) {
            console.warn('同步生成返回数据格式错误，没有找到新的配置实例ID');
            console.warn(e);
          }
        });
      } catch (e) {
        console.warn(e);
        generateList.forEach((item) => {
          item.taskStatus = 'failed';
          this.statusCounter.running -= 1;
          this.statusCounter.failed += 1;
        });
      } finally {
        this.$emit('update:isTasking', false);
      }
    },

    // 配置对比
    async compareConfiguration(row) {
      try {
        this.sliderData.isShow = true;
        this.sliderData.isLoading = true;
        const [releasedRes, previewRes] = await Promise.all([
          this.$store.dispatch('configInstance/ajaxGetLatestConfigInstance', {
            instId: row.inst_id,
            processId: row.bk_process_id,
            templateId: this.templateId,
          }),
          this.$store.dispatch('configVersion/ajaxPreviewConfigVersion', {
            data: {
              content: this.activeVersion.content,
              bk_process_id: row.bk_process_id,
            },
          }),
        ]);
        const language = this.activeVersion.file_format;
        releasedRes.data.released_config = releasedRes.data.released_config || {}; // 还没有下发配置
        this.sliderData.oldData = {
          content: releasedRes.data.released_config.content,
          language,
          time: releasedRes.data.released_config.created_at,
        };
        this.sliderData.newData = {
          content: previewRes.data,
          language,
          time: Date.now(),
        };
      } catch (e) {
        console.warn(e);
      } finally {
        this.sliderData.isLoading = false;
      }
    },
    // 关闭配置对比后清除数据
    handleCloseSlider() {
      this.sliderData.oldData = null;
      this.sliderData.newData = null;
    },
    // 查看配置
    handleViewConfig(row) {
      this.viewConfigData = [{
        id: row.config_instance_id,
        label: row.config_template.file_name,
      }];
    },
    // 版本提示
    getVersionTippy(item) {
      if (item.config_version_id === '-') {
        return {
          disabled: true,
        };
      }
      const updateBy = this.$t('更新人') + this.$t('：') + item.updated_by;
      const updateAt = this.$t('更新时间') + this.$t('：') + formatDate(item.updated_at);
      return {
        placement: 'right',
        content: `${updateBy}<br>${updateAt}`,
      };
    },
  },
};</script>

<style scoped lang="postcss">
  @import '../../css/variable.css';

  .instance-table-container {
    padding: 10px 60px 0;
    overflow: hidden;

    &:first-child {
      padding-top: 0;
    }

    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      height: 42px;
      padding: 0 10px;
      color: $newBlackColor2;
      background: $newGreyColor1;
      border-radius: 3px 3px 0 0;
      font-size: 12px;
      line-height: 20px;

      .header-left {
        display: flex;
        font-weight: bold;

        .icon-down-shape {
          width: 24px;
          font-size: 14px;
          margin-right: 6px;
          margin-top: 4px;
          cursor: pointer;
          transition: .2s;

          &.close {
            transform: rotate(-90deg);
            transition: .2s;
          }

          &:hover {
            color: $newMainColor;
          }
        }

        .config-name {
          font-size: 14px;
        }

        .version-to-dis {
          color: $newBlackColor3;

          .blue {
            color: $newMainColor;
            font-weight: bold;
            cursor: pointer;
          }
        }
      }

      .header-right-1 {
        display: flex;
        align-items: center;

        .version-selector {
          display: flex;
          align-items: center;
          cursor: pointer;

          &.selected {
            color: $newMainColor;
          }

          .gsekit-icon-filter-fill {
            font-size: 16px;
            margin-right: 4px;
          }
        }

        .split-line {
          width: 1px;
          height: 16px;
          margin: 0 12px;
          background-color: $newGreyColor;
        }
      }

      .header-right-2 {
        display: flex;
        align-items: center;

        .statue-counter-tips {
          padding-right: 14px;

          .num {
            font-weight: bold;
          }

          .success {
            color: #3fc06d;
          }

          .failed {
            color: #ea3636;
          }

          .loading {
            color: $newMainColor;
          }
        }
      }
    }

    .version-list {
      padding: 10px 40px;
      background-color: $newGreyColor3;
      border-left: 1px solid $newGreyColor1;
      border-right: 1px solid $newGreyColor1;

      .king-checkbox-group {
        display: flex;
        flex-flow: column;
      }

      .king-checkbox {
        line-height: 32px;

        >>> .bk-checkbox {
          margin-top: -2px;
        }

        .percent {
          font-size: 12px;
          color: $newBlackColor3;
        }
      }
    }

    .king-table {
      border-radius: 0 0 2px 2px;
      background-color: #fff;
    }

    .status-flag {
      padding: 0 10px;
      text-align: center;
      min-width: 60px;
      line-height: 52px;
      color: #dcdee5;
      background: #424242;
      font-size: 14px;
    }

    .create-time {
      padding-left: 20px;
      line-height: 52px;
      color: #c4c6cc;
      font-size: 14px;
    }
  }
</style>
