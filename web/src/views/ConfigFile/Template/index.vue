<template>
  <div v-bkloading="{ isLoading }" class="config-file-template-container">
    <router-view
      v-if="!isLoading"
      :selected-config="selectedConfig"
      :display-title="displayTitle"
      @selectConfig="selectConfig"
    ></router-view>
  </div>
</template>

<script>
export default {
  name: 'ConfigTemplate',
  data() {
    return {
      isLoading: true,
      selectedConfig: null,
    };
  },
  computed: {
    displayTitle() {
      return this.selectedConfig ? `${this.selectedConfig.template_name}(${this.selectedConfig.file_name})` : '';
    },
  },
  watch: {
    '$store.state.bizId'() { // 切换业务
      const { templateId } = this.$route.params;
      if (templateId) {
        // 切换业务后，该模板id不在该业务下，所以返回新业务的模板列表页面
        this.$store.commit('routeConfigTemplateList');
      } else {
        this.isLoading = true;
        this.$nextTick(() => {
          this.isLoading = false;
        });
      }
    },
  },
  created() {
    this.init();
  },
  methods: {
    init() {
      const { templateId } = this.$route.params;
      if (templateId) { // 进入配置功能页，需要获取配置文件数据
        this.getTemplateById(templateId);
      } else { // 进入列表页
        this.isLoading = false;
      }
    },
    async getTemplateById(templateId) {
      try {
        this.isLoading = true;
        const res = await this.$store.dispatch('configTemplate/ajaxGetConfigTemplateDetail', {
          templateId,
        });
        Object.assign(res.data, res.data.permission || {});
        res.data.config_template_id += '';
        this.selectedConfig = res.data;
      } catch (e) {
        console.warn(e);
        this.$store.commit('routeConfigTemplateList'); // 回到列表页
      } finally {
        this.isLoading = false;
      }
    },
    async selectConfig(templateDataOrId) {
      if (typeof templateDataOrId === 'string') {
        await this.getTemplateById(templateDataOrId);
        this.$store.commit('routeConfigTemplateVersionList', {
          templateId: templateDataOrId,
        });
      } else {
        this.selectedConfig = templateDataOrId;
      }
    },
  },
};
</script>

<style scoped lang="postcss">
  @import '../../../css/variable.css';

  .config-file-template-container {
    height: 100%;

    /deep/ .template-title {
      flex-shrink: 0;
      display: flex;
      align-items: center;
      padding: 18px 60px 20px;
      font-size: 16px;
      color: $newBlackColor1;

      .gsekit-icon {
        margin-right: 4px;
        font-size: 20px;
        transform: rotate(90deg);
        color: $newMainColor;
        cursor: pointer;

        &:hover {
          color: $newMainColor1;
        }
      }

      > .text {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }
  }
</style>
