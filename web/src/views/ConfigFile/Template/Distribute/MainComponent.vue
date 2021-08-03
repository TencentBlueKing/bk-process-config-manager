<template>
  <div class="main-component" :class="{ 'is-generate': isGeneratePage }">
    <div class="steps-container" v-if="!isGeneratePage">
      <bk-steps class="king-steps" :cur-step="curStep" :steps="steps"></bk-steps>
    </div>
    <div class="distribute-main">
      <SelectInstance
        v-show="curStep === 1"
        show-button
        :button-loading="tableLoading || generateButtonLoading"
        @init="handleSelectInstance"
        @buttonClick="handleSelectInstance" />
      <div v-show="curStep === 2" class="config-generate-button">
        <bk-button
          style="margin-right: 10px;"
          :loading="generateButtonLoading"
          :disabled="isDisableGenerateAndPrevious"
          @click="handleGenerate">
          {{ $t('全部重新生成') }}
        </bk-button>
        <!--<bk-button>{{ $t('批量对比') }}</bk-button>-->
      </div>
      <InstanceTable
        :cur-step="curStep"
        :selected-config="selectedConfig"
        :has-polling-task="hasPollingTask"
        :status-counter="statusCounter"
        :is-distributing="distributeButtonLoading"
        :is-generate-page="isGeneratePage"
        :instance-list="instanceList"
        :table-loading="tableLoading"
        @pageAdd="handlePageAdd"
        @updateStatus="handleStatusChange" />
    </div>
    <!-- 下面的操作按钮 -->
    <!-- 配置生成只有第一步(立即生成，取消) -->
    <!-- 配置下发第一步(下一步，取消)，第二步(立即下发,上一步，取消) -->
    <div
      v-show="!(isGeneratePage && curStep === 2)"
      class="distribute-footer"
      :class="{ 'is-button-fixed': isButtonFixed }">
      <!-- 第一步，配置生成 -->
      <bk-button
        v-show="curStep === 1"
        :loading="generateButtonLoading"
        :disabled="!instanceList.length || tableLoading"
        theme="primary"
        style="min-width: 120px;margin-right: 10px;"
        @click="handleGenerate">
        {{ isGeneratePage ? $t('立即生成') : $t('下一步') }}
      </bk-button>
      <!-- 第二步，配置下发 -->
      <div v-show="curStep === 2"
           v-bk-tooltips="{ content: $t('所有配置生成成功方能下发'), disabled: !isDisableDistribute }"
           class="button-container">
        <bk-button
          theme="primary"
          style="min-width: 120px;margin-right: 10px;"
          :loading="distributeButtonLoading"
          :disabled="isDisableDistribute"
          @click="handleDistribute">
          {{ $t('立即下发') }}
        </bk-button>
      </div>
      <bk-button
        v-show="curStep === 2"
        style="min-width: 86px;margin-right: 10px;"
        :disabled="isDisableGenerateAndPrevious"
        @click="handlePrevious">
        {{ $t('上一步') }}
      </bk-button>
      <bk-button style="min-width: 86px;" @click="handleCancel">
        {{ $t('取消') }}
      </bk-button>
    </div>
  </div>
</template>

<script>
import SelectInstance from '@/components/SelectInstance';
import InstanceTable from './InstanceTable';

export default {
  components: {
    SelectInstance,
    InstanceTable,
  },
  props: {
    selectedConfig: {
      type: Object,
      required: true,
    },
    type: {
      type: String,
      default: 'distribute',
      validator(value) {
        return ['distribute', 'generate'].includes(value);
      },
    },
  },
  data() {
    return {
      tableLoading: false, // 筛选结果请求表格内容中
      distributeButtonLoading: false, // 配置下发接口请求中
      generateButtonLoading: false, // 配置生成(全部)操作接口请求中
      hasPollingTask: false, // 是否有轮询任务
      isAllTaskSucceededOrFailed: false, // 轮询任务全部成功或失败
      jobId: null, // 配置生成任务 id
      isJobReady: false, // 为 true 时才可请求 task list
      jobTimer: null, // 配置生成之后查看 job 状态
      taskTimer: null, // job 状态完成之后查看 task 状态
      isButtonFixed: false,
      isDropdownMode: true, // 筛选表达式模式，默认筛选
      selectedScope: null, // 筛选表达式查询条件
      instanceList: [], // 已选择的实例列表
      instanceCounts: 0, // 当前页显示了多少条数据
      curStep: 1,
      steps: [
        { title: this.$t('选择实例'), icon: 1 },
        { title: this.$t('配置生成'), icon: 2 },
      ],
      statusCounter: {
        succeeded: 0, // 已生成
        failed: 0, // 生成失败
        pending: 0, // 生成中
        running: 0, // 生成中
      },
    };
  },
  computed: {
    isGeneratePage() { // 配置生成页面或配置下发页面
      return this.type === 'generate';
    },
    hasRunningTask() { // 有正在进行的任务
      return (this.statusCounter.pending + this.statusCounter.running) !== 0;
    },
    // 正在配置下发或有实例正在生成时禁用【全部生成】和【上一步】按钮
    isDisableGenerateAndPrevious() {
      return this.distributeButtonLoading || this.generateButtonLoading || this.hasRunningTask;
    },
    isDisableDistribute() { // 所有配置生成成功方能下发
      return this.generateButtonLoading || this.hasRunningTask;
    },
  },
  watch: {
    '$store.state.pageHeight'() {
      this.resizeHandler();
    },
    instanceList() {
      this.resizeHandler();
    },
  },
  beforeDestroy() {
    this.jobTimer && clearTimeout(this.jobTimer);
    this.taskTimer && clearTimeout(this.taskTimer);
  },
  methods: {
    // 表格更新、窗口尺寸变化时计算按钮是否吸附底部
    resizeHandler() {
      this.$nextTick(() => {
        this.isButtonFixed = this.$el.scrollHeight > this.$el.offsetHeight;
      });
    },
    // 根据筛选条件查询配置实例列表
    async handleSelectInstance(isDropdownMode, selectedScope) {
      try {
        this.isDropdownMode = isDropdownMode;
        this.selectedScope = selectedScope;
        this.tableLoading = true;
        const res = await this.$store.dispatch('configInstance/ajaxGetConfigInstanceList', {
          data: {
            [isDropdownMode ? 'scope' : 'expression_scope']: this.selectedScope,
            config_template_id: Number(this.$route.params.templateId),
          },
        });
        res.data.forEach((item) => {
          item.taskStatus = '';
        });
        this.instanceList = res.data;
      } catch (e) {
        console.warn(e);
        this.instanceList.splice(0);
      } finally {
        this.tableLoading = false;
      }
    },
    // 配置生成
    async handleGenerate() {
      if (!this.isGeneratePage && this.curStep === 1 && this.instanceList.every(item => item.status === 'generated')) {
        // 配置下发第一步下一步，如果已经生成配置就不重新生成了
        this.curStep = 2;
        this.instanceList.forEach((item) => {
          item.taskStatus = 'succeeded';
        });
        this.statusCounter = {
          succeeded: this.instanceList.length, // 已生成
          failed: 0, // 生成失败
          pending: 0, // 生成中
          running: 0, // 生成中
        };
        return;
      }
      try {
        this.jobId = null;
        this.isJobReady = false;
        this.generateButtonLoading = true;
        this.instanceList.forEach((item) => {
          item.taskStatus = 'running';
        });
        this.statusCounter = {
          succeeded: 0, // 已生成
          failed: 0, // 生成失败
          pending: 0, // 生成中
          running: this.instanceList.length, // 生成中
        };
        const res = await this.$store.dispatch('configTemplate/ajaxGenerateConfig', {
          data: {
            config_template_id: Number(this.$route.params.templateId),
            [this.isDropdownMode ? 'scope' : 'expression_scope']: this.selectedScope,
          },
        });
        this.jobId = res.data.job_id;
        this.pollingJobStatus();
        this.curStep = 2;
        this.hasPollingTask = true;
        this.isAllTaskSucceededOrFailed = false;
      } catch (e) {
        console.warn(e);
      } finally {
        this.generateButtonLoading = false;
      }
    },
    // job 状态轮询，job 执行成功后再轮询 task
    pollingJobStatus() {
      this.jobTimer = setTimeout(async () => {
        try {
          const res = await this.$store.dispatch('job/ajaxGetJobDetail', {
            jobId: this.jobId,
          });
          if (res.data.is_ready) {
            this.isJobReady = true;
            this.getTaskList();
          } else {
            this.pollingJobStatus();
          }
        } catch (e) {
          console.warn(e);
        }
      }, 2000);
    },
    // job 创建成功后拉取 task 列表
    async getTaskList() {
      try {
        // 清除之前的状态轮询，新的 task list 开启新一轮轮询
        this.taskTimer && clearTimeout(this.taskTimer);
        const res = await this.$store.dispatch('job/ajaxGetJobTaskList', {
          jobId: this.jobId,
          data: {
            page: 1,
            pagesize: this.instanceCounts,
          },
        });
        // 当轮询结束后，可以点击单个重新生成，会对 statusCounter 做出修改
        // 这个时候滚动分页可能请求 taskList，不应该回填总状态了，总状态由前端本地控制
        if (this.hasPollingTask) {
          this.statusCounter = res.data.status_counter;
        }
        const pollingTaskList = [];
        this.instanceList.slice(0, this.instanceCounts).forEach((instanceItem, instanceIndex) => {
          // 从 task list 里面找到对应实例的任务，后台保证顺序一致
          // const matchTaskItem = res.data.find(taskItem => {
          //     return taskItem.bk_process_id === instanceItem.bk_process_id
          //         && taskItem.extra_data.inst_id === instanceItem.inst_id
          // })
          const matchTaskItem = res.data.list[instanceIndex];
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
        if (this.judgeTaskDone()) {
          this.hasPollingTask = false;
        } else if (this.hasPollingTask) { // judgeTaskDone 返回 false 有可能是生成完成之后同步生成造成的
          this.pollingTaskStatus(pollingTaskList);
        }
      } catch (e) {
        console.warn(e);
      }
    },
    // task 轮询
    pollingTaskStatus(pollingTaskList) {
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
            const instanceItem = this.instanceList[pollingTask.instanceIndex];
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
          } else {
            this.pollingTaskStatus(newPollingTaskList);
          }
        } catch (e) {
          console.warn(e);
        }
      }, 2000);
    },
    // 根据 statusCounter 是否有进行中的任务判断 task 是否结束
    judgeTaskDone() {
      const result = (this.statusCounter.pending + this.statusCounter.running) === 0;
      if (result && !this.isAllTaskSucceededOrFailed) {
        // 轮询任务全部成功或失败可直接修改列表状态，下次滚动不用再请求 task_list 获取状态
        if (!this.statusCounter.failed) {
          this.isAllTaskSucceededOrFailed = true;
          this.instanceList.forEach((item) => {
            item.taskStatus = 'succeeded';
          });
        } else if (!this.statusCounter.succeeded) {
          this.isAllTaskSucceededOrFailed = true;
          this.instanceList.forEach((item) => {
            item.taskStatus = 'failed';
          });
        }
      }
      return result;
    },
    // 分页滚动加载数量增加了
    handlePageAdd(instanceCounts) {
      this.instanceCounts = instanceCounts;
      if (this.jobId !== null && this.isJobReady && !this.isAllTaskSucceededOrFailed) {
        // 需要更新 task_list
        this.getTaskList();
      }
    },
    // 配置下发
    async handleDistribute() {
      try {
        this.distributeButtonLoading = true;
        const res = await this.$store.dispatch('configTemplate/ajaxSetReleaseConfig', {
          data: {
            config_template_id: Number(this.$route.params.templateId),
            [this.isDropdownMode ? 'scope' : 'expression_scope']: this.selectedScope,
          },
        });
        this.$store.commit('routeTaskHistoryDetail', res.data.job_id);
      } catch (e) {
        console.warn(e);
        this.distributeButtonLoading = false;
      }
    },
    // 上一步
    handlePrevious() {
      this.curStep -= 1;
      // 清除任务信息
      this.jobId = null;
      this.isJobReady = false;
      this.hasPollingTask = false;
      this.isAllTaskSucceededOrFailed = false;
      // 这里重新拉取实例列表，以获取最新配置状态
      // 比如开始是 not_latest，后面生成后变成了 generated 还是 not_generated
      // 前端是不知道的，因为没有根据任务状态去修改配置状态的属性
      this.handleSelectInstance(this.isDropdownMode, this.selectedScope);
    },
    // 取消
    handleCancel() {
      if (this.$router.__from_name) {
        this.$router.back();
      } else {
        this.$store.commit('routeConfigTemplateList');
      }
    },
    handleStatusChange({ key, value }) {
      this.statusCounter[key] = value;
    },
  },
};
</script>

<style scoped lang="postcss">
  @import '../../../../css/variable.css';

  .main-component {
    position: relative;
    height: calc(100% - 60px);
    overflow: hidden;
    background-color: #fff;

    /* 配置下发的步骤组件 */
    .steps-container {
      display: flex;
      justify-content: center;
      height: 40px;
      margin: 0 auto;
      background-color: #f5f6fa;

      .king-steps {
        width: 372px;

        /deep/ .bk-step.current .bk-step-title {
          color: $newBlackColor1;
        }
      }
    }

    /* 选择实例筛选条件或按钮(height:72px)、表格(max-height:) */
    .distribute-main {
      .config-generate-button {
        display: flex;
        align-items: center;
        height: 72px;
        padding: 0 60px;
      }
    }

    /* 下面的操作按钮 */
    .distribute-footer {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 53px;
      padding-top: 20px;
      margin-top: -1px;

      &.is-button-fixed {
        padding-top: 0;
        border-top: 1px solid #dcdee5;
      }
    }

    /* 配置生成页面样式 */
    &.is-generate {
      background-color: #f5f6fa;

      .distribute-main {
        margin-top: -20px;
      }
    }
  }
</style>
