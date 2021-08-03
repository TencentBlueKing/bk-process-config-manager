<template>
  <div class="release-config">
    <div class="release-header">
      <i class="button-text gsekit-icon gsekit-icon-down-line" @click="$store.commit('routeProcessManageStatus')"></i>
      <span>{{ $t('配置下发') }}</span>
    </div>
    <ConfigDistribute :scope-data="scopeData" />
  </div>
</template>

<script>
import ConfigDistribute from '@/components/ConfigDistribute';

export default {
  name: 'ReleaseConfig',
  components: {
    ConfigDistribute,
  },
  data() {
    return {
      scopeData: {},
    };
  },
  watch: {
    '$store.state.bizId'() {
      this.$store.commit('routeProcessManageStatus');
    },
  },
  created() {
    // 通过路由获取参数
    const { isDropdownMode, scope } = this.$route.query;
    this.scopeData = {
      isDropdownMode: isDropdownMode === 'true' || isDropdownMode === true,
      selectedScope: JSON.parse(scope),
    };
  },
};
</script>

<style lang="postcss" scoped>
  .release-config {
    display: flex;
    flex-flow: column;
    height: 100%;
    background-color: #f5f6fa;

    .release-header {
      display: flex;
      flex-shrink: 0;
      align-items: center;
      color: #313238;
      font-size: 16px;
      line-height: 22px;
      padding: 18px 24px 20px;

      .gsekit-icon {
        font-weight: 700;
        margin-right: 7px;
        transform: rotate(90deg);
      }
    }

    >>> .config-file-template-distribute-container {
      height: calc(100% - 60px);
    }
  }
</style>
