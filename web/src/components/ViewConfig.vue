<template>
  <div class="view-config">
    <bk-sideslider
      :is-show.sync="isShow"
      :quick-close="true"
      :width="630"
      @hidden="onCloseSide">
      <div slot="header">{{ $t('配置文件详情') }}</div>
      <template slot="content">
        <div class="side-slider">
          <bk-tab
            v-show="instancesConfig && instancesConfig.length"
            :active.sync="active"
            type="unborder-card"
            @tab-change="handleTabChange">
            <bk-tab-panel
              v-for="config in instancesConfig"
              :label="config.label"
              :name="config.id"
              :key="config.id">
            </bk-tab-panel>
          </bk-tab>
          <div class="config-content" v-bkloading="{ isLoading: isDataLoading, opacity: .1 }">
            <ConfigFileDetail :config-file-detail="configFileDetail"></ConfigFileDetail>
            <CodeEditor
              :content="configFileDetail.content"
              :language="configFileDetail.line_separator"
              style="height: calc(100% - 154px); margin: 0 30px;" />
          </div>
        </div>
      </template>
    </bk-sideslider>
  </div>
</template>

<script>
import ConfigFileDetail from '@/views/TaskHistory/Detail/ConfigFileDetail';
import CodeEditor from '@/components/CodeEditor';
export default {
  components: {
    CodeEditor,
    ConfigFileDetail,
  },
  props: {
    instancesConfig: {
      type: Array,
      default: null,
    },
  },
  data() {
    return {
      configFileDetail: {},
      isDataLoading: true,
      isShow: false,
      active: null,
    };
  },
  watch: {
    instancesConfig(val) {
      if (val) {
        this.isShow = true;
        this.active = val[0].id;
        this.getConfigInstanceInfo(this.active);
      }
    },
  },
  methods: {
    // 获取配置实例详情
    async getConfigInstanceInfo(instanceId) {
      try {
        this.isDataLoading = true;
        const res = await this.$store.dispatch('configInstance/ajaxGetConfigInstanceDetail', {
          instanceId,
        });
        this.configFileDetail = res.data;
      } catch (error) {
        console.warn(error);
      } finally {
        this.isDataLoading = false;
      }
    },
    // 关闭配置面板
    onCloseSide() {
      this.configFileDetail = {};
      this.isShow = false;
      this.$emit('onCloseSide');
    },
    handleTabChange(val) {
      this.getConfigInstanceInfo(val);
    },
  },
};
</script>

<style lang="postcss" scoped>
  .view-config {
    /deep/ .bk-sideslider {
      .bk-sideslider-content {
        height: calc(100% - 60px);
      }
    }

    .side-slider {
      height: 100%;

      /deep/ .bk-tab {
        height: 60px;
        padding-top: 18px;

        .bk-tab-label-wrapper {
          padding-left: 18px;
        }
      }

      .config-content {
        height: calc(100% - 60px);
        padding-bottom: 20px;
      }
    }
  }
</style>
