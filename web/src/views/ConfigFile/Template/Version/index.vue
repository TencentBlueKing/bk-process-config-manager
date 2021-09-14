<template>
  <div class="config-file-template-version-container">
    <router-view
      :selected-config="selectedConfig"
      :display-title="displayTitle"
      :version-loading.sync="versionLoading"
      :version-list="versionList"
      :selected-version="selectedVersion"
      @clickVersionRow="handleClickVersionRow"
      @createNewVersion="handleCreateNewVersion"
      @updateVersionList="getVersionList"
    ></router-view>
  </div>
</template>

<script>
export default {
  name: 'TemplateVersion',
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
  data() {
    return {
      versionLoading: true,
      versionList: [],
    };
  },
  computed: {
    selectedVersion() {
      const { versionId } = this.$route.params;
      if (versionId === '0') { // 新建全新的草稿版本
        return {
          isDraftCreating: true,
          config_version_id: '0',
          description: this.$t('草稿'),
          content: '',
          file_format: 'python',
          is_draft: true,
        };
      }
      return this.versionList.find(item => item.config_version_id === this.$route.params.versionId) || null;
    },
  },
  created() {
    this.getVersionList();
  },
  methods: {
    async getVersionList(updateVersionId) {
      try {
        this.versionLoading = true;
        const res = await this.$store.dispatch('configTemplate/ajaxGetConfigVersionList', {
          templateId: this.$route.params.templateId,
        });
        if (res.data.length) {
          res.data.forEach((item) => {
            item.config_version_id += '';
          });
          this.versionList = res.data;

          if (updateVersionId) { // 更新列表并跳转到新的版本
            this.$nextTick(() => {
              if (this.$route.params.versionId) {
                this.$router.replace({
                  params: {
                    versionId: updateVersionId,
                  },
                });
              } else {
                this.$store.commit('routeConfigTemplateVersionDetail', {
                  templateId: this.$route.params.templateId,
                  versionId: updateVersionId,
                });
              }
            });
          } else {
            const { versionId } = this.$route.params;
            if (versionId) { // 详情页或预览页
              if (!res.data.some(item => item.config_version_id === versionId)) { // 路由请求的版本不存在，默认选中可用或第一项
                const targetVersion = res.data.find(item => item.is_active) || res.data[0];
                this.$router.replace({
                  params: {
                    versionId: targetVersion.config_version_id,
                  },
                  query: {
                    ...this.$route.query,
                  },
                });
              }
            } else {
              // 进入列表页
            }
          }
        }
      } catch (e) {
        console.warn(e);
        this.versionList.splice(0);
      } finally {
        this.versionLoading = false;
      }
    },
    handleClickVersionRow(row) {
      this.$store.commit('routeConfigTemplateVersionDetail', {
        templateId: this.$route.params.templateId,
        versionId: row.config_version_id,
      });
    },
    handleCreateNewVersion(version) {
      version.config_version_id += '';
      this.versionList.unshift(version);
    },
  },
};
</script>

<style scoped>
  @import '../../../../css/variable.css';

  .config-file-template-version-container {
    display: flow-root;
    height: 100%;
  }
</style>
