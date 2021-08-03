<template>
  <div class="config-file-template-distribute-container">
    <div class="template-title">
      <span class="gsekit-icon gsekit-icon-down-line" @click="backRoute"></span>
      <span class="text">{{ $t('配置下发') + $t('：') + displayTitle }}</span>
    </div>
    <ConfigDistribute :selected-config="selectedConfig" />
  </div>
</template>

<script>
import ConfigDistribute from '@/components/ConfigDistribute';

export default {
  name: 'TemplateDistribute',
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
  .config-file-template-distribute-container {
    display: flex;
    flex-flow: column;
    height: 100%;

    .template-title {
      flex-shrink: 0;
    }
  }
</style>
