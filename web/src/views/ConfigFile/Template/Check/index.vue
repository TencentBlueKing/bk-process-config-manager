<template>
  <div class="config-file-template-check-container">
    <div class="template-title">
      <span class="gsekit-icon gsekit-icon-down-line" @click="backRoute"></span>
      <span class="text">{{ $t('配置检查') + $t('：') + displayTitle }}</span>
    </div>
    <ConfigDistribute action="configCheck" :selected-config="selectedConfig" />
  </div>
</template>

<script>
import ConfigDistribute from '@/components/ConfigDistribute';

export default {
  name: 'TemplateConfigCheck',
  components: {
    ConfigDistribute,
  },
  props: {
    selectedConfig: {
      type: Object,
      required: true,
    },
    displayTitle: {
      type: String,
      required: true,
    },
  },
  methods: {
    backRoute() {
      if (this.$router.__from_name) {
        this.$router.back();
      } else {
        this.$store.commit('routeConfigTemplateList');
      }
    },
  },
};
</script>

<style scoped>
  .config-file-template-check-container {
    display: flex;
    flex-flow: column;
    height: 100%;

    .template-title {
      flex-shrink: 0;
    }
  }
</style>
