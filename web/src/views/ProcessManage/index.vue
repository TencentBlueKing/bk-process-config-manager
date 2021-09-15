<template>
  <div class="process-manage-container" v-test="'processManage'">
    <div class="navigation-content">
      <router-view v-if="isProcessStatusPage"></router-view>
    </div>
    <!-- <bk-navigation
      class="hack-king-navigation"
      navigation-type="top-bottom"
      head-height="0"
      :default-open="isNavigationOpen"
      @toggle-click="handleToggle">
      <template slot="menu">
        <bk-navigation-menu :default-active="activeNav">
          <bk-navigation-menu-item
            icon="gsekit-icon gsekit-icon-status-fill" id="processStatus" @click="onProcessStatus">
            {{ $t('进程状态') }}
          </bk-navigation-menu-item>
          <bk-navigation-menu-item
            icon="gsekit-icon gsekit-icon-process-manager-fill" id="processManage" @click="onProcessMessage">
            {{ $t('进程管理') }}
          </bk-navigation-menu-item>
        </bk-navigation-menu>
      </template>
      <div class="navigation-content">
        <router-view v-if="isProcessStatusPage"></router-view>
      </div>
    </bk-navigation> -->
  </div>
</template>

<script>
export default {
  name: 'ProcessPage',
  data() {
    return {
      isNavigationOpen: localStorage.getItem('isNavigationOpen') === '1',
      activeNav: 'processStatus',
      isProcessStatusPage: true,
    };
  },
  watch: {
    $route(val) {
      this.setActiveNav(val.name);
    },
    '$store.state.bizId'() {
      if (this.$route.name === 'process-manage-status') {
        this.isProcessStatusPage = false;
        this.$nextTick(() => {
          this.isProcessStatusPage = true;
        });
      }
    },
  },
  mounted() {
    this.setActiveNav(this.$route.name);
  },
  methods: {
    handleToggle(val) {
      localStorage.setItem('isNavigationOpen', val ? '1' : '0');
      // 代码编辑器需要重新 layout
      window.bus.$emit('navigation-toggle');
    },
    setActiveNav(val) {
      if (val === 'process-manage-status' || val === 'process-manage-release') {
        this.activeNav = 'processStatus';
      } else {
        this.activeNav = 'processManage';
      }
    },
    onProcessStatus() {
      this.$store.commit('routeProcessManageStatus');
    },
    onProcessMessage() {
      this.$store.commit('routeProcessManageManage');
    },
  },
};
</script>

<style lang="postcss" scoped>
  .process-manage-container {
    min-height: 100%;
  }

  .navigation-content {
    height: 100%;
    background-color: #f5f7fa;

    .process-status {
      padding: 18px 60px 30px;
    }
  }
</style>
