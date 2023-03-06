<template>
  <div class="history-detail" v-bkloading="{ isLoading: !Object.values(jobInfo).length }">
    <section class="detail-config">
      <div class="detail-config-header">
        <i class="button-text gsekit-icon gsekit-icon-down-line" @click="handleRouterClick"></i>
        <span>{{ $t('任务详情') + $t('：') }}</span>
        <template v-if="Object.values(jobInfo).length">
          <span>{{ jobObject[jobInfo.job_object] + jobAction[jobInfo.job_action] }}</span>
          <span :class="['perform-status', {
            'success': jobInfo.status === 'succeeded',
            'fail': jobInfo.status === 'failed'
          }]">
            {{ executionStatus[jobInfo.status] }}
          </span>
        </template>
        <template v-else> {{ '--' }}</template>
      </div>
      <div class="detail-config-couple">
        <DetailList :job-object="jobObject" :job-action="jobAction" :task-detail="jobInfo"></DetailList>
      </div>
    </section>
    <template v-if="jobInfo.extra_data && jobInfo.extra_data.failed_reason">
      <bk-exception class="exception-wrap-item" type="500">
        <span>{{ $t('创建任务失败') }}</span>
        <div class="text-wrap">
          {{ jobInfo.extra_data.failed_reason }}
        </div>
      </bk-exception>
    </template>
    <template v-else>
      <section class="detail-search">
        <div class="btn-section">
          <bk-button
            v-test="'retryAll'" @click="onAllRetry" :disabled="jobInfo.status !== 'failed'" :loading="retryLoading">
            {{ $t('重试所有失败') }}
          </bk-button>
          <bk-dropdown-menu
            trigger="click"
            ref="dropdownCopy"
            font-size="medium"
            :disabled="['running', 'pending'].includes(jobInfo.status) || copyLoading"
            @show="dropdownShow"
            @hide="dropdownHide">
            <bk-button
              slot="dropdown-trigger"
              class="copy-dropdown-btn"
              v-test.common="'more'"
              :disabled="['running', 'pending'].includes(jobInfo.status)">
              <span class="icon-down-wrapper">
                <span>{{ $t('复制') }}</span>
                <i :class="['bk-icon icon-angle-down', { 'icon-flip': isShowCopy }]"></i>
              </span>
            </bk-button>
            <ul class="bk-dropdown-list" slot="dropdown-content">
              <li v-for="(copyType, index) in copyTypeList" :key="index + Date.now()">
                <a
                  href="javascript:"
                  v-test.common="'moreItem'"
                  :test-key="copyType.key || 'all'"
                  @click.prevent.stop="handleCopy(copyType.key)">
                  {{ copyType.name }}
                </a>
              </li>
            </ul>
          </bk-dropdown-menu>
        </div>
        <bk-search-select
          ref="searchSelect"
          v-test.common="'searchSelect'"
          v-model="searchSelectValue"
          :show-condition="false"
          :data="searchSelectData"
          @show-menu="handleSearchSelectShowMenu"
          @change="handleSearchSelectChange"></bk-search-select>
      </section>
      <section class="tab-header" v-if="statusTabList.length">
        <div
          v-for="item in statusTabList"
          v-test="'tableTabItem'"
          :key="item.err_code"
          :class="['tab-item', { 'active': selectedTabCode === item.err_code }]"
          @click="handleTabChange(item)">
          <span v-if="item.err_code === 0" class="status-icon generated-status"></span>
          <span v-else-if="item.err_code === 1" class="status-icon pending-status"></span>
          <span v-else-if="item.err_code === 3" class="status-icon failed-status"></span>
          <span v-else-if="item.err_code === 4" class="status-icon ignored-status"></span>
          <svg v-else-if="item.err_code === 2" class="status-icon running-status" aria-hidden="true">
            <use xlink:href="#gsekit-icon-loading"></use>
          </svg>
          <span v-else class="status-icon other-status"></span>
          <span class="tab-item-name" v-bk-overflow-tips>{{ item.message }}</span>
          <span class="tab-item-count">{{ item.count }}</span>
        </div>
      </section>
      <section class="detail-table">
        <bk-table
          v-bkloading="{ isLoading: isTableLoading }"
          auto-scroll-to-top
          ext-cls="king-table"
          :max-height="$store.state.pageHeight - 345"
          :data="taskList"
          :pagination="pagination"
          @page-change="handlePageChange"
          @page-limit-change="handlePageLimitChange">
          <bk-table-column :label="$t('集群')" prop="set_name" :render-header="renderFilterHeader" show-overflow-tooltip>
            <template slot-scope="{ row }">
              <span>{{ row.bk_set_name || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column
            :label="$t('模块')" prop="template_name" :render-header="renderFilterHeader" show-overflow-tooltip>
            <template slot-scope="{ row }">
              <span>{{ row.bk_module_name || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('服务实例')" min-width="180" prop="server_instance" show-overflow-tooltip>
            <template slot-scope="{ row }">
              <span>{{ row.name || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column
            :label="$t('进程别名')"
            prop="process_name"
            show-overflow-tooltip
            :render-header="renderFilterHeader">
            <template slot-scope="{ row }">
              <span>{{ row.bk_process_name || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column label="process_id" prop="bk_process_id" show-overflow-tooltip>
            <template slot-scope="{ row }">
              <span>{{ row.bk_process_id || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column label="inst_id" prop="inst_id" width="70">
            <template slot-scope="{ row }">
              <span>{{ row.extra_data.inst_id || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('进程优先级')" prop="priority">
            <template slot-scope="{ row }">
              <span>{{ row.priority || row.priority === 0 ? row.priority : '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('内网IP')" prop="bk_host_innerip" width="125">
            <template slot-scope="{ row }">
              <span>{{ row.bk_host_innerip || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('执行耗时')" prop="timeout" width="100" show-overflow-tooltip>
            <template slot-scope="{ row }">
              <span>{{ row.timeout || '--' }}</span>
            </template>
          </bk-table-column>
          <bk-table-column :label="$t('执行状态')" width="140" prop="status" :render-header="renderFilterHeader">
            <template slot-scope="{ row }">
              <!-- 执行状态 -->
              <div class="status-info">
                <StatusView v-if="row.status === 'succeeded'" type="success" :text="$t('执行成功')" />
                <template v-else-if="row.status === 'failed'">
                  <GenerateFailed :failed-reason="row.extra_data.failed_reason" :solutions="row.extra_data.solutions" />
                </template>
                <template v-else-if="row.status === 'ignored'">
                  <GenerateFailed
                    status-type="ignored"
                    :text="$t('已忽略')"
                    :failed-reason="row.extra_data.failed_reason"
                    :solutions="row.extra_data.solutions">
                  </GenerateFailed>
                </template>
                <StatusView v-else type="loading" :text="$t('正在执行')" />
              </div>
            </template>
          </bk-table-column>
          <!-- <bk-table-column :label="$t('操作')" :min-width="jobInfo.job_object !== 'process' ? 145 : 100"> -->
          <bk-table-column v-if="showOperateColumn" :label="$t('操作')" :min-width="100">
            <div slot-scope="{ row }" @click.stop>
              <bk-button v-if="showDiffBtn" theme="primary" text @click="compareConfiguration(row)">
                {{ $t('配置对比') }}
              </bk-button>
              <template v-else>
                <!-- <template v-if="jobInfo.job_object !== 'process'"> -->
                <bk-popover :disabled="!!row.instancesConfig || ['running', 'pending'].includes(row.status)"
                            :content="$t('没有绑定配置实例，暂无法查看')">
                  <bk-button
                    :disabled="!row.instancesConfig || ['running', 'pending'].includes(row.status)"
                    theme="primary"
                    text
                    style="margin-right: 6px;"
                    @click="onCheckConfig(row)">
                    {{ $t('查看配置') }}
                  </bk-button>
                </bk-popover>
                <!-- </template> -->
                <!-- 暂时隐藏单行重试 -->
                <!-- <bk-popover
                  :disabled="row.status !== 'failed' || row.extra_data.retryable"
                  ext-cls="failed-tips"
                  placement="bottom"
                  theme="light"
                  :max-width="500">
                  <bk-button
                      :disabled="row.status !== 'failed' || !row.extra_data.retryable"
                      theme="primary"
                      text
                      @click="onRetry(row)">
                      {{ $t('重试') }}</bk-button>
                  <template slot="content">
                      <div class="failed-message">
                          <div class="message-text">{{ '失败信息：' }}</div>
                          <div v-html="row.extra_data.failed_reason || '--'"></div>
                      </div>
                      <div class="resolve-message" v-if="row.extra_data.solutions && row.extra_data.solutions.length">
                          <div class="message-text">{{ '解决方案：' }}</div>
                          <div v-for="(soluteItem, index) in row.extra_data.solutions" :key="index">
                              <div class="solute-item">
                              <span class="solute-item-order">{{ index + 1 + '.' }}</span>
                              <div class="solute-item-content" v-html="soluteItem.html"></div>
                              </div>
                          </div>
                      </div>
                  </template>
                </bk-popover> -->
              </template>
            </div>
          </bk-table-column>
          <TableException
            slot="empty"
            :delay="isTableLoading"
            :type="tableEmptyType"
            @empty-clear="emptySearchClear" />
        </bk-table>
      </section>
    </template>
    <ViewConfig
      :instances-config="instancesConfig"
      @onCloseSide="onCloseSide">
    </ViewConfig>
    <!-- 配置对比 -->
    <bk-sideslider
      :is-show.sync="sliderData.isShow"
      :quick-close="true"
      :width="1200"
      @hidden="handleCloseSlider">
      <div class="config-contrast-header" slot="header">
        <span>{{ $t('配置对比') }}</span>
        <span class="divide-line">{{ '-' }}</span>
        <span class="template-name">
          {{ sliderData.instancesConfig.name + '(' + sliderData.instancesConfig.label + ')' }}
        </span>
      </div>
      <div v-bkloading="{ isLoading: sliderData.isLoading }" style="height: calc(100vh - 60px);" slot="content">
        <SidesliderDiff v-if="sliderData.oldData" :old-data="sliderData.oldData" :new-data="sliderData.newData">
          <template slot="leftTitle">
            <div class="status-flag">{{ $t('最后下发') }}</div>
            <div class="create-time">{{ $t('下发时间') + $t('：') + (formatDate(sliderData.oldData.time) || '--') }}</div>
          </template>
          <template slot="rightTitle">
            <div class="status-flag">{{ $t('现网配置') }}</div>
            <div class="create-time">{{ $t('检查时间') + $t('：') + (formatDate(sliderData.newData.time) || '--') }}</div>
          </template>
        </SidesliderDiff>
      </div>
    </bk-sideslider>
  </div>
</template>

<script>
import DetailList from './DetailList';
import tableHeaderMixins from '@/components/FilterHeader/table-header-mixins';
import ViewConfig from '@/components/ViewConfig';
import { performTime, modifyFormatDate, copyText, formatDate } from '@/common/util';
import GenerateFailed from '@/components/GenerateFailed';
import SidesliderDiff from '@/components/SidesliderDiff';

export default {
  name: 'HistoryDetail',
  components: {
    ViewConfig,
    DetailList,
    GenerateFailed,
    SidesliderDiff,
  },
  mixins: [tableHeaderMixins],
  props: {
    selectedConfig: {
      type: Object,
      default: null,
    },
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
  },
  data() {
    const executionStatus = {
      succeeded: this.$t('执行成功'),
      failed: this.$t('执行失败'),
      running: this.$t('正在执行'),
      pending: this.$t('等待中'),
    };
    return {
      statusTabList: [],
      selectedTabCode: null,
      taskList: [], // 任务详情列表
      jobInfo: {}, // 任务详情
      pagination: {
        current: 1,
        count: 0,
        limit: 50,
      },
      instancesConfig: [],
      executionStatus,
      isTableLoading: false,
      isDataLoading: false,
      retryLoading: false,
      timer: null,
      executedList: ['succeeded', 'failed', 'ignored'],
      copyLoading: false,
      copyTypeList: [
        { name: this.$t('所有IP'), key: '' },
        { name: this.$t('被忽略IP'), key: 'ignored' },
        { name: this.$t('失败IP'), key: 'failed' },
        { name: this.$t('成功IP'), key: 'succeeded' },
      ],
      isShowCopy: false,
      activeVersion: {},
      sliderData: {
        isShow: false,
        isLoading: false,
        instancesConfig: {},
        oldData: null, // 配置对比数据
        newData: null, // 配置对比数据
      },
      templateId: null, // 记录上一次拉取版本信息的id, 不做重复拉取
      formatDate,
    };
  },
  computed: {
    showOperateColumn() {
      return this.jobInfo.job_object !== 'process';
    },
    showDiffBtn() {
      return this.selectedTabCode === 4103007;
    },
    tableEmptyType() {
      return this.searchSelectValue.length ? 'search-empty' : 'empty';
    },
  },
  watch: {
    selectedConfig: {
      handler(val) {
        if (!val) return;
        const info = this.setInfoDataType(val);
        if (info.is_ready && !info.extra_data.failed_reason) {
          // 任务详情统计
          this.getJobTaskStatistics();
          // 获取过滤数据
          this.getFilterCondition();
        }
        // 任务类型
        this.jobInfo = info;
        this.isTableLoading = true;
      },
      immediate: true,
    },
  },
  beforeDestroy() {
    clearTimeout(this.timer);
  },
  methods: {
    // 任务详情统计（按错误码）
    async getJobTaskStatistics() {
      try {
        const res = await this.$store.dispatch('job/ajaxGetJobTaskStatistics', {
          jobId: this.$route.params.jobId,
        });
        this.statusTabList = res.data || [];
        const errCodeList = this.statusTabList.map(item => item.err_code);
        if (!errCodeList.includes(this.selectedTabCode)) {
          this.selectedTabCode = res.data[0].err_code;
        }
        // 获取任务历史详情列表
        this.getTaskHistoryDetail();
      } catch (error) {
        console.warn(error);
      }
    },
    // 获取任务历史详情列表
    async getTaskHistoryDetail() {
      try {
        const data = this.getSearchParams();
        const res = await this.$store.dispatch('job/ajaxGetJobTaskList', {
          jobId: this.$route.params.jobId,
          data,
        });
        const { list, count } = res.data;
        // 任务详情列表计算执行耗时
        list.forEach((item) => {
          // 将表格所需字段从内部挪到外部
          const processInfo = item.extra_data.process_info;
          item.bk_set_name = processInfo.set.bk_set_name;
          item.bk_module_name = processInfo.module.bk_module_name;
          item.name = processInfo.service_instance.name;
          item.bk_process_name = processInfo.process.bk_process_name;
          item.bk_host_innerip = processInfo.host.bk_host_innerip;
          item.priority = processInfo.process.priority;
          if (this.executedList.includes(item.status)) {
            item.timeout = performTime(item.start_time, item.end_time);
          }
          // 处理配置实例信息
          const instancesConfig = item.extra_data.config_instances;
          if (instancesConfig && instancesConfig.length) {
            item.instancesConfig = [];
            instancesConfig.forEach((configItem) => {
              item.instancesConfig.push({
                name: configItem.template_name,
                label: configItem.file_name,
                id: configItem.id,
              });
            });
          }
        });
        this.taskList = list;
        this.pagination.count = count;
        // 任务状态是否查询
        if (['pending', 'running'].includes(this.jobInfo.status)) {
          this.getJobStatus();
        } else {
          this.retryLoading = false;
        }
      } catch (error) {
        console.warn(error);
      } finally {
        this.isTableLoading = false;
      }
    },
    setInfoDataType(info) {
      // 处理开始时间
      info.start_time = modifyFormatDate(info.start_time);
      // 处理结束时间
      info.end_time = modifyFormatDate(info.end_time);
      // 任务详情计算执行耗时
      info.timeout = performTime(info.start_time, info.end_time);
      // 环境类型
      const setEnv = info.expression_scope.bk_set_env;
      let setEevName = '';
      switch (setEnv) {
        case '1':
          setEevName = this.$t('测试');
          break;
        case '2':
          setEevName = this.$t('体验');
          break;
        case '3':
          setEevName = this.$t('正式');
          break;
      }
      info.setEevName = setEevName;
      return info;
    },
    async getSelectedConfig() {
      const { jobId } = this.$route.params;
      if (!jobId) return;
      const res = await this.$store.dispatch('job/ajaxGetJobDetail', { jobId });
      const info = this.setInfoDataType(res.data);
      this.jobInfo = info;
    },
    // 任务状态查询
    getJobStatus() {
      try {
        clearTimeout(this.timer);
        this.timer = setTimeout(async () => {
          this.getSelectedConfig();
          this.getJobTaskStatistics();
        }, 3000);
      } catch (error) {
        console.warn(error);
      }
    },
    // 获取过滤数据
    async getFilterCondition() {
      try {
        const res = await this.$store.dispatch('meta/ajaxGetTaskFilterCondition', {
          jobId: this.$route.params.jobId,
        });
        const filterData = [];
        for (const [key, value] of Object.entries(res.data)) {
          const params = {
            children: value,
            multiable: true,
          };
          switch (key) {
            case 'module':
              params.id = 'template_name';
              params.name = this.$t('模块');
              break;
            case 'process':
              params.id = 'process_name';
              params.name = this.$t('进程别名');
              break;
            case 'set':
              params.id = 'set_name';
              params.name = this.$t('集群');
              break;
            case 'status_choices':
              params.id = 'status';
              params.name = this.$t('状态');
          }
          filterData.push(params);
        }
        this.filterData = filterData;
        this.searchSelectData = filterData;
      } catch (error) {
        console.warn(error);
      }
    },
    // 生成搜索参数
    getSearchParams() {
      const params = {
        page: this.pagination.current,
        pagesize: this.pagination.limit,
        err_code: this.selectedTabCode,
      };
      if (this.searchSelectValue.length) {
        this.searchSelectValue.forEach((item) => {
          switch (item.id) {
            case 'set_name':
              params.bk_set_ids = item.values.map(val => val.id);
              break;
            case 'template_name':
              params.bk_module_ids = item.values.map(val => val.id);
              break;
            case 'process_name':
              params.bk_process_names = item.values.map(val => val.id);
              break;
            case 'status':
              params.statuses = item.values.map(val => val.id);
          }
        });
      }
      return params;
    },
    onCheckConfig(row) {
      this.instancesConfig = row.instancesConfig;
    },
    onCloseSide() {
      this.instancesConfig = null;
    },
    // tab栏切换
    handleTabChange(item) {
      this.pagination.current = 1;
      this.selectedTabCode = item.err_code;
      this.isTableLoading = true;
      this.getTaskHistoryDetail();
    },
    dropdownShow() {
      this.isShowCopy = true;
    },
    dropdownHide() {
      this.isShowCopy = false;
    },
    // 复制ip
    async handleCopy(key) {
      try {
        this.copyLoading = true;
        this.$refs.dropdownCopy.hide();
        const res = await this.$store.dispatch('job/ajaxGetSearchIp', {
          jobId: this.$route.params.jobId,
          status: key,
        });
        if (res) {
          const content = { theme: 'error', message: this.$t('没有符合条件的IP') };
          if (res.data && res.data.length) {
            const ipStr = res.data.map(item => item.bk_host_innerip).join('\n');
            const result = copyText(ipStr);
            if (result) {
              Object.assign(content, {
                theme: 'success',
                message: this.$t('IP复制成功', { num: res.data.length }),
              });
            }
          }
          this.$bkMessage(content);
        }
      } catch (error) {
        console.warn(error);
      } finally {
        this.copyLoading = false;
      }
    },
    // 重试失败
    async onRetry(row) {
      try {
        row.status = 'running';
        this.$store.dispatch('job/ajaxRetryJob', {
          jobId: row.job_id,
          data: {
            job_task_id_list: [row.id],
          },
        }).then(() => {
          this.getJobStatus();
        });
      } catch (error) {
        console.warn(error);
      }
    },
    // 重试所有失败
    async onAllRetry() {
      try {
        this.retryLoading = true;
        this.taskList.forEach((item) => {
          if (item.status === 'failed') {
            item.status = 'running';
          }
        });
        await this.$store.dispatch('job/ajaxRetryJob', {
          jobId: this.jobInfo.id,
          data: {
            job_task_id_list: [],
          },
        }).then(() => {
          this.getJobStatus();
        });
      } catch (error) {
        console.warn(error);
      }
    },
    // 小箭头路由处理
    handleRouterClick() {
      const fromName = this.$router.__from_name;
      if (fromName) {
        if (fromName === 'process-manage-release') {
          this.$store.commit('routeProcessManageStatus');
        } else if (fromName === 'config-file-template-distribute') {
          this.$store.commit('routeConfigTemplateList');
        } else {
          this.$router.back();
        }
      } else {
        this.$store.commit('routeTaskHistoryList');
      }
    },
    handlePageChange(page) {
      this.isTableLoading = true;
      this.pagination.current = page;
      this.getTaskHistoryDetail();
    },
    handlePageLimitChange(limit) {
      this.isTableLoading = true;
      this.pagination.current = 1;
      this.pagination.limit = limit;
      this.getTaskHistoryDetail();
    },
    // 配置对比 - 获取版本信息
    async getActiveVersion() {
      try {
        const versionRes = await this.$store.dispatch('configTemplate/ajaxGetConfigVersionList', {
          templateId: this.templateId,
        });
        this.activeVersion = versionRes.data.find(item => item.is_active);
      } catch (e) {
        console.warn(e);
      }
    },
    // 配置对比
    async compareConfiguration(row) {
      try {
        this.sliderData.isShow = true;
        this.sliderData.isLoading = true;
        this.sliderData.instancesConfig = row.instancesConfig[0] || {};
        const templateId = row.extra_data.config_template_ids[0];
        const isIdenticalTemp = templateId === this.templateId;
        const promiseList = [
          this.$store.dispatch('configInstance/ajaxGetConfigInstanceDetail', { instanceId: this.sliderData.instancesConfig.id }),
        ];
        if (!isIdenticalTemp) {
          this.templateId = templateId;
          // 获取版本信息 - 拿到配置的language
          promiseList.push(this.$store.dispatch('configTemplate/ajaxGetConfigVersionList', { templateId }));
        }
        const [instanceRes, versionRes] = await Promise.all(promiseList);
        if (!isIdenticalTemp) {
          this.activeVersion = versionRes.data.find(item => item.is_active) || {};
        }
        const language = this.activeVersion.file_format;
        // config_snapshot_info快照 实例的实际配置
        const { content, created_at, config_snapshot_info: snapshot = {} } = instanceRes.data;
        this.sliderData.newData = {
          content: snapshot.content,
          language,
          time: snapshot.created_at,
        };
        this.sliderData.oldData = {
          content,
          language,
          time: created_at,
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
    emptySearchClear() {
      this.isTableLoading = true;
      this.searchSelectValue = [];
      this.handleSearchSelectChange(this.searchSelectValue);
    },
  },
};
</script>

<style lang="postcss" scoped>
  .history-detail {
    height: 100%;

    .detail-config {
      width: 100%;
      padding: 18px 0px 20px 60px;
      background: #f0f1f5;

      .detail-config-header {
        height: 21px;
        display: flex;
        align-items: center;
        color: #313238;
        font-size: 16px;
        margin-bottom: 20px;

        .gsekit-icon {
          font-weight: 700;
          margin-right: 7px;
          transform: rotate(90deg);
        }

        .perform-status {
          padding: 2px 4px;
          background: #3a84ff;
          border-radius: 2px;
          text-align: center;
          font-weight: 700;
          color: #fff;
          font-size: 12px;
          transform: scale(.8);
        }

        .success {
          background: #3fc06d;
        }

        .fail {
          background: #ea3636;
        }
      }

      .detail-config-couple {
        width: 100%;
      }
    }

    .detail-search {
      padding: 0px 60px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      background-color: #f0f1f5;

      .bk-button {
        border: 1px solid #c4c6cc;
        margin-right: 10px;
      }

      .copy-dropdown-btn {
        margin-right: 0;
      }

      /deep/ .bk-search-select {
        width: 500px;
        border: 1px solid #c4c6cc;
        background: #fff;
      }
    }

    .detail-table {
      height: calc(100% - 273px);
      padding: 0 60px 20px;
      margin-top: 20px;
    }

    /deep/ .bk-loading {
      width: calc(100% - 2px);
      height: calc(100% - 2px);
    }

    /deep/ .exception-wrap-item {
      height: calc(100% - 139px);
      padding-top: 50px;

      .text-wrap {
        margin-top: 15px;
        font-size: 14px;
        color: #979ba5;
      }
    }
  }

  .tab-header {
    height: 42px;
    padding: 0 60px;
    display: flex;
    align-items: center;
    color: #63656e;
    background-color: #f0f1f5;
    background-image: linear-gradient(transparent 41px,#dcdee5 0);

    .tab-item {
      width: 200px;
      height: 42px;
      display: flex;
      align-items: center;
      font-size: 14px;
      cursor: pointer;
      background: #e1e3eb;
      border: 1px solid transparent;
      border-radius: 6px 6px 0 0;
      margin-right: 8px;
      padding: 0 12px;

      .status-icon {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 6px;
        flex-shrink: 0;
      }

      .generated-status {
        background: #e5f6ea;
        border: 1px solid #3fc06d;
      }

      .failed-status,
      .other-status {
        background: #ffe6e6;
        border: 1px solid #ea3636;
      }

      .ignored-status {
        background: #ffe8c3;
        border: 1px solid #ff9c01;
      }

      .pending-status {
        background: #f0f1f5;
        border: 1px solid #c4c6cc;
      }

      .running-status {
        width: 16px;
        height: 16px;
      }

      .tab-item-name {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .tab-item-count {
        flex-shrink: 0;
        height: 17px;
        min-width: 14px;
        line-height: 17px;
        padding: 0 4px;
        color: #fff;
        font-size: 12px;
        font-weight: 600;
        background: #c4c6cc;
        border-radius: 8px;
        margin-left: 6px;
      }

      &.active {
        border: 1px solid #dcdee5;
        border-bottom-color: #fff;
        background: #fff;
        color: #313238;

        .tab-item-count {
          background: #c4c6cc;
          color: #63656e;
        }
      }
    }
  }
</style>
