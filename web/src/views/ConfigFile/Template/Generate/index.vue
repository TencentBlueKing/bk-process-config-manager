<template>
  <div class="config-file-template-generate-container">
    <div class="template-title">
      <span class="gsekit-icon gsekit-icon-down-line" @click="backRoute"></span>
      <span class="text">{{ $t('配置生成') + $t('：') + displayTitle }}</span>
    </div>
    <MainComponent type="generate" :selected-config="selectedConfig" />
  </div>
</template>

<script>
import MainComponent from '../Distribute/MainComponent';

export default {
  name: 'TemplateGenerate',
  components: {
    MainComponent,
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
  .config-file-template-generate-container {
    height: 100%;
  }
</style>
