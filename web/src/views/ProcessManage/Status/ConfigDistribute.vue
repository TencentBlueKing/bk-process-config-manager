<template>
  <bk-sideslider
    :title="titleName"
    :is-show="true"
    :width="!isContrast ? 630 : 1197"
    :before-close="onCloseSidesLider"
    :quick-close="true">
    <div class="from-area" slot="content">
      <div class="editor-header">
        <div :class="['common-form-item', { 'default-width': !isContrast }]">
          <label class="required">{{ $t('配置模板') }}</label>
          <bk-select
            v-test="'tempSelect'"
            v-model="templateId"
            :clearable="false"
            :disabled="isBatch || isGenerateLoading"
            @change="handleSelectChange">
            <bk-option
              v-for="item in templateList"
              :key="item.config_template_id"
              :id="item.config_template_id"
              :name="item.showName">
            </bk-option>
          </bk-select>
          <bk-button
            :loading="isGenerateLoading"
            :diasbled="isReleaseLoading"
            :theme="'primary'"
            v-test="'configGenerate'"
            @click="setSyncGenerateConfig(true)">
            <div class="generate-btn">
              <i class="swither-icon gsekit-icon gsekit-icon-swither-small"></i>
              <span>{{ $t('生成') }}</span>
            </div>
          </bk-button>
          <template v-if="!configInfo.is_latest">
            <span class="update-tip">{{ $t('模版有更新，请重新生成') }}</span>
            <i class="new-generate-icon"></i>
          </template>
        </div>
        <div v-if="isContrast" class="common-form-item expand-width">
          <DiffNav
            class="diff-nav-container"
            :diff-count="diffCount"
            @previous="jumpPreviousChange"
            @next="jumpNextChange" />
        </div>
      </div>
      <div class="editor-content" v-bkloading="{ isLoading: isDataLoading, opacity: .1 }">
        <div class="editor-title">
          <div :class="['common-form-editor', { 'default-width': !isContrast }]">
            <div class="real-time" v-if="isContrast">{{ $t('实时') }}</div>
            <div class="editor-info">
              <div>{{ configInfo.file_name || '--' }}</div>
              <div>
                {{ $t('生成时间') }}
                <template v-if="isContrast">
                  {{ releasedConfig.created_at ? modifyFormatDate(releasedConfig.created_at) : '--'}}
                </template>
                <template v-else>
                  {{ generatedConfig.created_at ? modifyFormatDate(generatedConfig.created_at) : '--'}}
                </template>
              </div>
            </div>
          </div>
          <div class="common-form-editor" v-if="isContrast">
            <div class="pre-populated">{{ $t('预生成') }}</div>
            <div class="editor-info">
              <div>{{ configInfo.file_name || '--' }}</div>
              <div>
                {{ $t('生成时间') }}
                <template v-if="isContrast">
                  {{ generatedConfig.created_at ? modifyFormatDate(generatedConfig.created_at) : '--'}}
                </template>
                <template v-else>
                  {{ releasedConfig.created_at ? modifyFormatDate(releasedConfig.created_at) : '--'}}
                </template>
              </div>
            </div>
          </div>
        </div>
        <DiffEditor
          v-if="isContrast"
          ref="diffEditorRef"
          style="height: calc(100% - 73px);"
          :old-data="releasedConfig"
          :new-data="generatedConfig"
          :diff-count.sync="diffCount" />
        <CodeEditor
          v-else
          :content="generatedConfig.content"
          :language="generatedConfig.language"
          style="height: calc(100% - 73px);" />
      </div>
      <div class="king-btn-group" v-if="!isBatch">
        <bk-popover :disabled="isDataLoading || Boolean(generatedConfig.created_at)"
                    :content="$t('请重新生成')">
          <bk-button
            v-test="'configRelease'"
            :disabled="isDataLoading || !generatedConfig.created_at"
            :loading="isReleaseLoading"
            theme="primary"
            @click="onConfigDistribute">
            {{ $t('配置下发') }}
          </bk-button>
        </bk-popover>
        <bk-button
          v-test="'configContrast'"
          @click="onConfigContrast"
          :disabled="isDataLoading || !generatedConfig.content"
          :class="{ 'pressed': isContrast }">
          {{ $t('配置对比') }}
        </bk-button>
        <bk-button @click="onCancel">
          {{ $t('取消') }}
        </bk-button>
      </div>
    </div>
  </bk-sideslider>
</template>

<script>
import CodeEditor from '@/components/CodeEditor';
import DiffEditor from '@/components/DiffEditor';
import DiffNav from '@/components/DiffNav';
import { modifyFormatDate } from '@/common/util';

export default {
  components: {
    CodeEditor,
    DiffEditor,
    DiffNav,
  },
  props: {
    processDetail: {
      type: Object,
      default: () => ({}),
    },
    selectedScope: {
      type: Object,
      default: () => ({}),
    },
    isDropdownMode: {
      type: Boolean,
      default: true,
    },
    titleName: {
      type: String,
      default: '',
    },
    isBatch: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      modifyFormatDate,
      templateList: [], // 下拉列表
      configInfo: {}, // 配置信息
      generatedConfig: {
        content: '',
        language: '',
        created_at: '',
      },
      releasedConfig: {
        content: '',
        language: '',
        created_at: '',
      },
      templateId: '', // 下拉框默认选中id
      isContrast: false, // 是否为配置对比
      isGenerateLoading: false,
      isDataLoading: false,
      isReleaseLoading: false,
      diffCount: 0,
    };
  },
  watch: {
    processDetail: {
      handler(val) {
        this.templateList = val.config_templates.map((item) => {
          this.$set(item, 'showName', item.template_name + this.$t('（') + item.file_name + this.$t('）'));
          return item;
        });
        this.templateId = this.templateList[0].config_template_id;
        // 获取进程相关配置信息
        this.getConfigInfo();
      },
      immediate: true,
    },
  },
  methods: {
    // 获取进程相关配置信息
    async getConfigInfo() {
      try {
        this.isDataLoading = true;
        const res = await this.$store.dispatch('configInstance/ajaxGetLatestConfigInstance', {
          templateId: this.templateId,
          processId: this.processDetail.bk_process_id,
        });
        const selectInfo = this.templateList.find(item => item.config_template_id === this.templateId);
        this.configInfo = res.data || {};
        if (this.isContrast) {
          this.isContrast = false;
          this.$nextTick(() => {
            this.isContrast = true;
          });
        }
        this.configInfo.file_name = selectInfo.file_name;
        this.generatedConfig = this.configInfo.generated_config || {};
        this.releasedConfig = this.configInfo.released_config || {};
        if (!Object.keys(this.generatedConfig).length) {
          this.setSyncGenerateConfig();
        }
      } catch (error) {
        console.warn(error);
        this.isDataLoading = false;
      } finally {
        this.isDataLoading = false;
        this.isGenerateLoading = false;
      }
    },
    // 配置模板下拉改变
    handleSelectChange(val) {
      this.templateId = val;
      this.isContrast = false;
      this.getConfigInfo();
    },
    // 关闭侧滑
    onCloseSidesLider() {
      this.$emit('closeSideSlider');
    },
    // 配置下发
    async onConfigDistribute() {
      try {
        this.isReleaseLoading = true;
        const res = await this.$store.dispatch('configTemplate/ajaxSetReleaseConfig', {
          data: {
            config_template_id: this.templateId,
            [this.isDropdownMode ? 'scope' : 'expression_scope']: this.selectedScope,
          },
        });
        this.$store.commit('routeTaskHistoryDetail', res.data.job_id);
      } catch (error) {
        console.warn(error);
        this.isReleaseLoading = false;
      } finally {
        this.isReleaseLoading = false;
      }
    },
    // 配置对比
    onConfigContrast() {
      this.isContrast = !this.isContrast;
    },
    // 取消
    onCancel() {
      this.$emit('closeSideSlider');
    },
    // 同步配置生成
    async setSyncGenerateConfig(isClickBtn) {
      try {
        this.isDataLoading = true;
        this.isGenerateLoading = true;
        const res = await this.$store.dispatch('configTemplate/ajaxSyncGenerateConfig', {
          data: {
            bk_process_id: this.processDetail.bk_process_id,
          },
          templateId: this.templateId,
        });
        const matchTaskItem = res.data[0] || {};
        if (matchTaskItem.status === 'succeeded') {
          // 重新获取配置信息  提示执行成功信息
          await this.getConfigInfo();
          if (!isClickBtn) return true;
          this.$bkMessage({
            message: this.$t('配置生成成功'),
            theme: 'success',
          });
        } else {
          // 关闭loading  提示执行失败信息
          this.isDataLoading = false;
          this.isGenerateLoading = false;
          if (!isClickBtn) return true;
          this.$bkMessage({
            message: this.$t('配置生成失败'),
            theme: 'error',
          });
        }
      } catch (error) {
        console.warn(error);
        this.isGenerateLoading = false;
        this.isDataLoading = false;
      }
    },
    jumpNextChange() {
      this.$refs.diffEditorRef.diffNavigator.next();
    },
    jumpPreviousChange() {
      this.$refs.diffEditorRef.diffNavigator.previous();
    },
  },
};
</script>

<style lang='postcss' scoped>
  /deep/ .bk-sideslider-content {
    height: 100%;

    .from-area {
      padding: 30px 30px 0;
      height: calc(100% - 60px);
    }
  }

  .editor-header {
    display: flex;
    align-items: center;
  }

  .editor-title {
    background: #323232;
    display: flex;
    align-items: center;
    box-shadow: 0 2px 4px 0 rgba(0, 0, 0, .3);
    z-index: 1;
    position: relative;

    .common-form-editor {
      width: calc(50% - 15px);
      display: flex;

      .real-time,
      .pre-populated {
        min-width: 60px;
        text-align: center;
        color: #dcdee5;
        padding-top: 10px;
        background: #424242;
        line-height: 24px;
        font-size: 14px;
      }

      .editor-info {
        width: 100%;
        line-height: 24px;
        font-size: 14px;
        color: #c4c6cc;
        border-radius: 2px 2px 0px 0px;
        padding: 10px 20px 15px;
      }
    }
  }

  .editor-content {
    height: calc(100% - 58px);
  }

  .common-form-item {
    width: calc(50% - 15px);
    display: flex;
    align-items: center;
    margin-bottom: 25px;
    position: relative;

    .required {
      position: relative;
      font-size: 14px;
      color: #63656e;
      flex-shrink: 0;

      &::after {
        content: '*';
        position: absolute;
        top: 3px;
        right: -10px;
        color: #ff2602;
      }
    }

    .bk-button {
      border-radius: 0 2px 2px 0;
      padding: 0 16px 0 8px;

      .generate-btn {
        display: flex;
        align-items: center;

        .swither-icon {
          font-size: 20px;
        }

        span {
          margin-left: 4px;
        }
      }
    }

    .bk-select {
      margin-left: 24px;
      width: 412px;
      border-radius: 2px 0 0 2px;
      border-right: 0;
    }

    .update-tip {
      position: absolute;
      top: 32px;
      left: 80px;
      font-size: 12px;
      color: #ea3636;
    }

    .new-generate-icon {
      position: absolute;
      top: -3px;
      right: -2px;
      height: 6px;
      width: 6px;
      border: 1px solid #fff;
      border-radius: 50%;
      background: #ea3636;
    }

    .diff-nav-container {
      margin-left: 40px;
    }
  }

  .default-width {
    width: 100% !important;
  }

  .expand-width {
    justify-content: flex-end;
    width: calc(50% + 15px);
  }

  .king-btn-group {
    height: 60px;
    line-height: 60px;
    border-top: 1px solid #dcdee5;

    .bk-button {
      margin-right: 10px;
    }

    .pressed {
      background: #dcdee5;
      color: #63656e;
    }

    /deep/ .bk-tooltip {
      line-height: 32px;
    }
  }

</style>
