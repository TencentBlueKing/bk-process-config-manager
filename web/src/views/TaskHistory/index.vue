<template>
  <div class="task-history-container">
    <router-view
      v-if="isHistoryListPage"
      :selected-config="selectedConfig"
      :job-object="jobObject"
      :job-action="jobAction"
      :set-env="setEnv"
      @getTaskDeatail="getTaskDeatail">
    </router-view>
  </div>
</template>
<script>
export default {
  name: 'HistoryPage',
  data() {
    const jobObject = {
      configfile: '配置文件',
      process: '进程',
    };
    const jobAction = {
      generate: this.$t('生成'),
      start: this.$t('启动'),
      stop: this.$t('停止'),
      restart: this.$t('重启'),
      release: this.$t('下发'),
      diff: this.$t('检查'),
      reload: this.$t('重载'),
      force_stop: this.$t('强制停止'),
      set_auto: this.$t('托管'),
      unset_auto: this.$t('取消托管'),
    };
    const setEnv = {
      1: this.$t('测试'),
      2: this.$t('体验'),
      3: this.$t('正式'),
    };
    return {
      jobObject,
      jobAction,
      setEnv,
      selectedConfig: null,
      timer: null,
      isHistoryListPage: true,
    };
  },
  watch: {
    '$store.state.bizId'() {
      const { jobId } = this.$route.params;
      if (jobId) {
        this.$store.commit('routeTaskHistoryList');
      }
      if (this.$route.name === 'task-history-list') {
        this.isHistoryListPage = false;
        this.$nextTick(() => {
          this.isHistoryListPage = true;
        });
      }
    },
  },
  beforeDestroy() {
    clearTimeout(this.timer);
  },
  created() {
    this.init();
  },
  methods: {
    init() {
      const { jobId } = this.$route.params;
      if (jobId) {
        this.getSelectedConfig();
      }
    },
    async getSelectedConfig() {
      const { jobId } = this.$route.params;
      if (!jobId) return;
      const res = await this.$store.dispatch('job/ajaxGetJobDetail', { jobId });
      this.selectedConfig = res.data;
      if (res.data.is_ready) {
        clearTimeout(this.timer);
      } else {
        this.timer = setTimeout(() => {
          this.getSelectedConfig();
        }, 2000);
      }
    },
    getTaskDeatail(row) {
      this.selectedConfig = row;
      if (!this.selectedConfig.is_ready) {
        this.$nextTick(() => {
          this.getSelectedConfig();
        });
      }
    },
  },
};
</script>
<style scoped>
    .task-history-container {
      min-height: 100%;
    }
</style>
