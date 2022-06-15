<template>
  <div
    class="version-detail-container" v-test="'versionDetail'" v-bkloading="{ isLoading: versionLoading, opacity: .1 }">
    <template v-if="selectedVersion">
      <div class="template-title">
        <span class="gsekit-icon gsekit-icon-down-line" @click="backToVersionList"></span>
        <span class="text">{{ $t('版本详情') + $t('：') + displayTitle }}</span>
      </div>

      <!-- 详情页核心内容 -->
      <div class="detail-main-container">
        <!-- 左边主内容 -->
        <div class="detail-left-panel" :class="isFullScreen && 'full-screen'"
             :style="{ width: showRightPanel ? `calc(100% - ${rightPanelWidth}px)` : '100%' }">
          <div class="code-header">
            <!-- 版本ID 和描述 -->
            <div class="code-header-left">
              <span v-bk-overflow-tips="{ distance: 24 }" class="id-and-description text-overflow-row">
                #{{ selectedVersion.config_version_id }} {{ selectedVersion.description }}
              </span>
              <TagDraft v-if="selectedVersion.is_draft" dark />
              <TagAvailable v-else-if="selectedVersion.is_active" dark />
            </div>
            <!-- 草稿：高亮风格、全屏 -->
            <div v-if="selectedVersion.is_draft" class="code-header-right">
              <span>{{ $t('高亮风格') }}</span>
              <bk-select
                v-model="codeLanguage"
                v-test="'highlight'"
                class="king-select dark"
                ext-popover-cls="dark"
                :clearable="false">
                <bk-option id="python" name="python"></bk-option>
                <bk-option id="yaml" name="yaml"></bk-option>
                <bk-option id="json" name="json"></bk-option>
                <bk-option id="javascript" name="javascript"></bk-option>
              </bk-select>
              <span
                v-bk-tooltips="{ content: $t('全屏'), theme: 'black-arrow' }"
                :class="`gsekit-icon gsekit-icon-${isFullScreen ? 'exit-full-screen-line' : 'full-screen-line-line'}`"
                @click="isFullScreen = !isFullScreen">
              </span>
            </div>
            <!-- 可用：复制并新建 -->
            <div v-else class="code-header-right">
              <bk-button
                class="king-button king-button-copy"
                v-test="'copy'"
                theme="primary"
                icon="plus-line"
                @click="copyAndCreate">{{ $t('复制并新建') }}
              </bk-button>
              <bk-button class="king-button dark" v-test="'preview'" @click="handleOpenPreview">
                {{ $t('预览') }}
              </bk-button>
            </div>
          </div>
          <div class="editor-main">
            <CodeEditor
              ref="codeEditorRef"
              :content="selectedVersion.content"
              :language="codeLanguage"
              :readonly="!selectedVersion.is_draft"
              :eol="endOfLine"
              @markers="handleUpdateMarkers"
              @change="handleEditorContentChange" />

            <div v-if="showMarkersAside" class="code-marker-aside" :style="{ height: markerAsideHeight + 'px' }">
              <div class="code-marker">
                <ul ref="codeMarkerRef">
                  <li v-for="(marker, index) in currentEditorMarkers" :key="index" class="code-marker-item">
                    <i class="marker-icon bk-icon icon-close-circle-shape"></i>
                    <span class="marker-message" v-if="marker.type === 'msg'">{{ marker.message }}</span>
                    <template v-else>
                      <span class="marker-owner">[{{ marker.owner }}]</span>
                      <span class="marker-message">{{ marker.message }}</span>
                      <span class="marker-code" v-if="marker.code">[{{ marker.code }}]</span>
                      <span class="marker-range">({{ marker.lineRange }})</span>
                    </template>
                  </li>
                </ul>
              </div>
              <DragIcon prop="marker" placement="top" :class="isMarkerDragActive && 'active'" @dragBegin="dragBegin" />
            </div>
          </div>
        </div>
        <!-- 右边变量和预览 -->
        <div v-show="showRightPanel" class="detail-right-panel" :style="{ width: rightPanelWidth + 'px' }">
          <VariableComponent v-show="showVariablePanel" @close="showVariablePanel = false" />
          <PreviewComponent
            v-show="showPreviewPanel"
            :template-id="templateId"
            :show-preview-panel="showPreviewPanel"
            :preview-language="codeLanguage"
            :preview-content="currentEditorContent"
            :preview-content-cache.sync="previewContentCache"
            ref="previewRef"
            @close="showPreviewPanel = false"
            @markers="handleUpdateMarkers" />
          <DragIcon :class="isDragActive && 'active'" @dragBegin="dragBegin" />
        </div>
      </div>
      <div v-if="selectedVersion.is_draft" class="code-footer">
        <bk-button
          v-bk-tooltips="emptyContentTips"
          v-test="'save'"
          theme="primary"
          class="king-button"
          :class="(!currentEditorContent || !canSave) && 'dark is-disabled'"
          @click="handleSave">
          {{ $t('保存') }}
        </bk-button>
        <bk-button
          v-bk-tooltips="emptyContentTips"
          style="margin-right: 60px;"
          class="king-button dark"
          v-test="'saveDraft'"
          :class="!currentEditorContent && 'is-disabled'"
          :loading="saveDraftLoading"
          @click="handleSaveDraft">
          {{ $t('暂存草稿') }}
        </bk-button>
        <bk-button
          v-bk-tooltips="disableDiffTips"
          class="king-button dark"
          :class="!usableVersion && 'is-disabled'"
          v-test="'diff'"
          @click="handleDiff">
          {{ $t('对比') }}
        </bk-button>
        <bk-button class="king-button dark" v-test="'showVariable'" @click="handleOpenVariable">
          {{ $t('变量') }}
        </bk-button>
        <bk-button
          v-bk-tooltips="rePreviewTips"
          style="margin-right: 60px;"
          class="king-button dark"
          :class="{ 'is-draft-updated': isDraftUpdated && showPreviewPanel }"
          v-test="'preview'"
          @click="handleOpenPreview">
          {{ $t('预览') }}
        </bk-button>
        <bk-button class="king-button dark" @click="backToVersionList">{{ $t('取消') }}</bk-button>
      </div>

      <bk-sideslider :is-show.sync="showDiff" :quick-close="true" :title="$t('版本对比')" :width="1200">
        <DraftDiff
          v-if="showDiff"
          slot="content"
          :version-list="versionList"
          :draft-version="selectedVersion"
          :new-data="{ content: currentEditorContent, language: codeLanguage }"
          @coverSuccess="handleDiffCoverSuccess" />
      </bk-sideslider>
      <SaveDialog
        :show.sync="showSaveDialog"
        :loading="saveLoading"
        @confirm="handleConfirmSave" />
      <CoverDialog
        :show.sync="showCoverDialog"
        :version-list="versionList"
        :cover-version="selectedVersion"
        @close="showCoverDialog = false"
        @coverSuccess="handleCopyCoverSuccess" />
    </template>
  </div>
</template>

<script>
import TagAvailable from '../TagAvailable';
import TagDraft from '../TagDraft';
import DragIcon from '@/components/Common/DragIcon';
import VariableComponent from './Variable';
import PreviewComponent from './Preview';
import CodeEditor from '@/components/CodeEditor';
import DraftDiff from './DraftDiff';
import SaveDialog from './SaveDialog';
import CoverDialog from './CoverDialog';
import { formatDate } from '@/common/util';

export default {
  name: 'VersionDetail',
  components: {
    TagAvailable,
    TagDraft,
    DragIcon,
    VariableComponent,
    PreviewComponent,
    CodeEditor,
    DraftDiff,
    SaveDialog,
    CoverDialog,
  },
  props: {
    selectedConfig: {
      type: Object,
      required: true,
    },
    displayTitle: {
      type: String,
      default: '',
    },
    versionLoading: {
      type: Boolean,
      required: true,
    },
    versionList: {
      type: Array,
      required: true,
    },
    selectedVersion: {
      type: Object,
      default: null,
    },
  },
  data() {
    const mainWidth = document.body.offsetWidth - 120; // 代码区域宽度
    const rightPanelWidth = Math.floor(mainWidth * 0.382);
    return {
      formatDate,
      codeLanguage: 'python', // 高亮风格
      currentEditorContent: '', // 当前草稿输入的内容
      currentEditorMarkers: [], // 当前编译器错误信息
      markerAsideHeight: 0,
      minMarkerHeight: 48,
      maxMarkerHeight: 400,
      isMarkerDragActive: false,
      dragType: '',
      saveLoading: false, // 保存弹窗按钮loading
      isFullScreen: false, // 全屏

      rightPanelWidth, // 右侧变量、预览面板宽度
      minWidth: 500, // 右侧面板最小宽度
      maxWidth: 900, // 右侧面板最大宽度
      isDragActive: false, // 正在拖动面板宽度
      showVariablePanel: false, // 显示帮助信息
      showPreviewPanel: false, // 显示预览信息
      previewContentCache: '',

      showDiff: false, // 草稿和可用代码对比
      showSaveDialog: false, // 保存确认弹窗
      showCoverDialog: false, // 覆盖草稿弹窗
      saveDraftLoading: false, // 暂存草稿按钮loading
    };
  },
  computed: {
    showRightPanel() {
      return this.showVariablePanel || this.showPreviewPanel;
    },
    showMarkersAside() {
      return !!this.currentEditorMarkers.length;
    },
    isDraftUpdated() { // 草稿有更新，需要重新预览哦
      return this.previewContentCache && this.currentEditorContent !== this.previewContentCache;
    },
    versionId() {
      return this.$route.params.versionId;
    },
    templateId() {
      return this.$route.params.templateId;
    },
    usableVersion() { // 有可用的版本才可 DIFF
      return this.versionList.find(item => item.is_active);
    },
    usableCodeData() {
      return {
        content: this.usableVersion.content,
        language: this.usableVersion.file_format,
      };
    },
    draftCodeData() {
      return {
        content: this.currentEditorContent,
        language: this.codeLanguage,
      };
    },
    rePreviewTips() {
      return {
        theme: 'black-arrow',
        content: this.$t('草稿有更新，请重新预览'),
        disabled: !this.isDraftUpdated || !this.showPreviewPanel,
      };
    },
    disableDiffTips() {
      return {
        theme: 'black-arrow',
        content: this.$t('暂无可供对比的版本'),
        disabled: Boolean(this.usableVersion),
      };
    },
    canSave() { // 预览成功后才可以保存
      return this.currentEditorContent === this.previewContentCache;
    },
    emptyContentTips() {
      const tips = {
        theme: 'black-arrow',
        content: '',
        disable: true,
      };
      if (!this.currentEditorContent) {
        tips.content = this.$t('配置模板内容为空');
        tips.disable = false;
      } else if (!this.canSave) {
        tips.content = this.$t('请预览成功后再保存');
        tips.disable = false;
      }
      return tips;
    },
    endOfLine() {
      return this.selectedConfig && this.selectedConfig.line_separator
        ? this.selectedConfig.line_separator
        : 'LF';
    },
  },
  watch: {
    selectedVersion: { // 以前有切换功能，现在暂时只是做一些初始化
      handler(val) {
        if (val) {
          this.codeLanguage = val.file_format || 'python';
          if (this.$route.query.preview) {
            this.showVariablePanel = false;
            this.showPreviewPanel = true;
          } else if (val.is_draft) {
            this.showVariablePanel = true;
            this.showPreviewPanel = false;
          }
        }
      },
      immediate: true,
    },
    isFullScreen() {
      window.bus.$emit('resize', true);
    },
    showRightPanel() {
      window.bus.$emit('resize', true);
    },
    rightPanelWidth() {
      window.bus.$emit('resize');
    },
    showMarkersAside(val) {
      this.$nextTick(() => {
        if (val) {
          if (this.$refs.codeMarkerRef) {
            const height = this.$refs.codeMarkerRef.clientHeight;
            this.markerAsideHeight = height > 168 ? 200  : height + 32;
          }
        }
        window.bus.$emit('resize', true);
      });
    },
  },
  mounted() {
    window.addEventListener('keydown', this.handleKeydown);
  },
  beforeDestroy() {
    window.removeEventListener('keydown', this.handleKeydown);
  },
  beforeRouteLeave(from, to, next) { // 离开路由
    if (this.selectedVersion.is_draft && this.selectedVersion.content !== this.currentEditorContent) {
      // 草稿修改后未保存
      this.$bkInfo({
        title: this.$t('是否离开当前页') + this.$t('？'),
        subTitle: this.$t('离开将会导致未保存信息丢失'),
        confirmFn: () => {
          // 离开前回填避免重复触发钩子
          this.$refs.codeEditorRef.setValue(this.selectedVersion.content);
          next();
        },
      });
    } else {
      next();
    }
  },
  methods: {
    handleKeydown(e) {
      if (e.code === 'Escape' && this.isFullScreen) {
        this.isFullScreen = false;
      }
    },

    handleEditorContentChange(val) {
      this.currentEditorContent = val;
    },
    handleUpdateMarkers(markers = []) {
      this.currentEditorMarkers = markers;
    },

    // 保存草稿为可用
    handleSave() {
      if (!this.currentEditorContent || !this.canSave) {
        return;
      }
      this.showSaveDialog = true;
    },
    async handleConfirmSave(description) {
      if (!this.currentEditorContent) {
        return;
      }
      if (this.selectedVersion.config_version_id === '0') {
        return this.createNewActiveVersion(description);
      }
      try {
        this.saveLoading = true;
        const res = await this.$store.dispatch('configVersion/ajaxUpdateConfigVersion', {
          versionId: this.selectedVersion.config_version_id,
          data: {
            description,
            content: this.currentEditorContent,
            file_format: this.codeLanguage,
            is_active: true, // 保存为可用版本
            is_draft: false,
          },
        });
        if (this.usableVersion) {
          this.usableVersion.is_active = false;
        }
        Object.assign(this.selectedVersion, {
          description: res.data.description,
          content: res.data.content,
          file_format: res.data.codeLanguage,
          updated_at: res.data.updated_at,
          updated_by: res.data.updated_by,
          is_active: true,
          is_draft: false,
        });
        this.messageSuccess(this.$t('保存成功'));
        this.showSaveDialog = false;
        this.backToVersionList();
      } catch (e) {
        console.warn(e);
      } finally {
        this.saveLoading = false;
      }
    },
    async createNewActiveVersion(description) {
      try {
        this.saveLoading = true;
        const res = await this.$store.dispatch('configTemplate/ajaxCreateNewConfigVersion', {
          templateId: this.templateId,
          data: {
            description,
            content: this.currentEditorContent,
            file_format: this.codeLanguage,
            is_active: true,
          },
        });
        if (this.usableVersion) {
          this.usableVersion.is_active = false;
        }
        this.$emit('createNewVersion', res.data);
        this.messageSuccess(this.$t('成功创建新版本'));
        this.showSaveDialog = false;
        this.$set(this.selectedVersion, 'is_draft', false); // 确保能够离开路由
        this.backToVersionList();
      } catch (e) {
        console.warn(e);
      } finally {
        this.saveLoading = false;
      }
    },

    // 暂存草稿
    async handleSaveDraft() {
      if (!this.currentEditorContent) {
        return;
      }
      if (this.selectedVersion.config_version_id === '0') {
        return this.createNewDraftVersion();
      }
      try {
        this.saveDraftLoading = true;
        const res = await this.$store.dispatch('configVersion/ajaxUpdateConfigVersion', {
          versionId: this.versionId,
          data: {
            description: this.selectedVersion.description,
            content: this.currentEditorContent,
            file_format: this.codeLanguage,
            is_active: false,
            is_draft: true,
          },
        });
        Object.assign(this.selectedVersion, {
          description: res.data.description,
          content: res.data.content,
          file_format: res.data.codeLanguage,
          updated_at: res.data.updated_at,
          updated_by: res.data.updated_by,
        });
        this.messageSuccess(this.$t('保存成功'));
      } catch (e) {
        console.warn(e);
      } finally {
        this.saveDraftLoading = false;
      }
    },
    async createNewDraftVersion() {
      try {
        this.saveDraftLoading = true;
        const res = await this.$store.dispatch('configTemplate/ajaxCreateNewConfigVersion', {
          templateId: this.templateId,
          data: {
            description: this.selectedVersion.description,
            content: this.currentEditorContent,
            file_format: this.codeLanguage,
          },
        });
        this.$emit('createNewVersion', res.data);
        this.messageSuccess(this.$t('保存成功'));
        this.$store.commit('routeConfigTemplateVersionDetail', {
          templateId: this.templateId,
          versionId: res.data.config_version_id,
        });
      } catch (e) {
        console.warn(e);
      } finally {
        this.saveDraftLoading = false;
      }
    },

    // 对比
    handleDiff() {
      if (!this.usableVersion) {
        return;
      }
      this.showDiff = true;
    },
    async handleDiffCoverSuccess(res) {
      Object.assign(this.selectedVersion, {
        description: res.data.description,
        content: res.data.content,
        file_format: res.data.codeLanguage,
        updated_at: res.data.updated_at,
        updated_by: res.data.updated_by,
      });
      this.showDiff = false;
      this.messageSuccess(this.$t('修改成功'));
    },

    // 变量
    handleOpenVariable() {
      this.showVariablePanel = true;
      this.showPreviewPanel = false;
    },
    // 预览
    handleOpenPreview() {
      if (this.showPreviewPanel) {
        this.$refs.previewRef.handleRefresh();
      } else {
        this.showPreviewPanel = true;
        this.showVariablePanel = false;
      }
    },

    // 返回版本列表
    backToVersionList() {
      this.$store.commit('routeConfigTemplateVersionList', {
        templateId: this.templateId,
      });
    },

    // 复制并新建，
    async copyAndCreate() {
      if (this.versionList.some(item => item.is_draft)) { // 是否覆盖草稿
        this.showCoverDialog = true;
      } else { // 直接以此克隆并新增草稿
        try {
          this.$emit('update:versionLoading', true);
          const res = await this.$store.dispatch('configVersion/ajaxCreateConfigVersion', {
            versionId: this.versionId,
            data: {
              description: this.selectedVersion.description,
            },
          });
          this.messageSuccess(this.$t('成功创建新版本'));
          this.$emit('updateVersionList', res.data.config_version_id.toString());
        } catch (e) {
          console.warn(e);
          this.$emit('update:versionLoading', false);
        }
      }
    },
    // 覆盖草稿，实际修改
    handleCopyCoverSuccess(versionId) {
      this.showCoverDialog = false;
      this.$emit('updateVersionList', versionId);
    },

    // 拖动右边栏的宽度
    dragBegin(e, prop) {
      this.dragType = prop;
      if (prop === 'default') {
        this.isDragActive = true;
        this.currentWidth = this.rightPanelWidth;
        this.currentScreenX = e.screenX;
      } else {
        this.isMarkerDragActive = true;
        this.currentHeight = this.markerAsideHeight;
        this.currentScreenY = e.screenY;
      }
      window.addEventListener('mousemove', this.dragMoving, { passive: true });
      window.addEventListener('mouseup', this.dragStop, { passive: true });
    },
    dragMoving(e) {
      if (this.dragType === 'default') {
        const newWidth = this.currentWidth - e.screenX + this.currentScreenX;
        if (newWidth < this.minWidth) {
          this.rightPanelWidth = this.minWidth;
        } else if (newWidth > this.maxWidth) {
          this.rightPanelWidth = this.maxWidth;
        } else {
          this.rightPanelWidth = newWidth;
        }
      } else {
        const newHeight = this.currentHeight - e.screenY + this.currentScreenY;
        if (newHeight < this.minMarkerHeight) {
          this.markerAsideHeight = this.minMarkerHeight;
        } else if (newHeight > this.maxMarkerHeight) {
          this.markerAsideHeight = this.maxMarkerHeight;
        } else {
          this.markerAsideHeight = newHeight;
        }
      }
    },
    dragStop() {
      this.isDragActive = false;
      this.isMarkerDragActive = false;
      this.currentWidth = null;
      this.currentScreenX = null;
      this.dragType = '';
      this.currentHeight = null;
      this.currentScreenY = null;
      window.removeEventListener('mousemove', this.dragMoving);
      window.removeEventListener('mouseup', this.dragStop);
      this.handleErrorResize();
    },
    handleErrorResize() {
      window.bus.$emit('resize', true);
    },
  },
};
</script>

<style scoped lang="postcss">
  @import '../../../../../css/variable.css';
  @import '../../../../../css/mixins/scroll.css';

  .version-detail-container {
    position: relative;
    display: flex;
    flex-flow: column;
    height: 100%;

    .detail-main-container {
      display: flex;
      height: 100%;
      margin: 0 60px;
      background: #323232;
      overflow: hidden;

      .detail-left-panel {
        display: flex;
        flex-flow: column;

        .code-header {
          flex-shrink: 0;
          display: flex;
          align-items: center;
          justify-content: space-between;
          height: 52px;
          line-height: 20px;
          background-color: #323232;
          box-shadow: 0 2px 4px 0 rgba(0, 0, 0, .3);
          z-index: 1;

          .code-header-left {
            display: flex;
            align-items: center;
            padding-right: 20px;
            overflow: hidden;

            .id-and-description {
              font-size: 16px;
              color: #dcdee5;
              padding: 0 6px 0 24px;
            }
          }

          .code-header-right {
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            font-size: 12px;
            color: #c4c6cc;

            .king-select {
              width: 120px;
              margin: 0 16px 0 8px;
            }

            .gsekit-icon {
              font-size: 16px;
              margin-right: 20px;
              cursor: pointer;

              &:hover {
                color: #fff;
              }
            }

            .king-button {
              margin-right: 10px;

              &:last-child {
                margin-right: 20px;
              }
            }

            .king-button-copy {
              /deep/ .icon-plus-line {
                top: 0;
                font-size: 16px;
              }
            }
          }
        }
        .editor-main {
          display: flex;
          flex-direction: column;
          height: 100%;
          overflow: hidden;
        }
        .code-marker-aside {
          flex-shrink: 0;
          position: relative;
          min-height: 48px;
          padding-top: 16px;
          border-left: 4px solid #b34747;
          background: #212121;
          overflow: hidden;
          box-shadow: 0 0px 2px rgb(0, 0, 0, .3);
        }
        .code-marker {
          height: 100%;
          padding: 0 20px 16px 40px;
          line-height: 16px;
          font-size: 12px;
          overflow: auto;
          @mixin scroller;
        }
        .code-marker-item {
          position: relative;
          & + .code-marker-item {
            margin-top: 12px;
          }
        }
        .marker-icon {
          position: absolute;
          left: -20px;
          top: 2px;
          color: #b34747;
        }
        .marker-message {
          color: #dcdee5;
        }
        .marker-owner,
        .marker-code,
        .marker-range {
          color: #979ba5;
        }

        &.full-screen {
          position: fixed;
          top: 0;
          left: 0;
          width: 100% !important;
          height: 100%;
          z-index: 1000;
          margin: 0;
        }
      }

      .detail-right-panel {
        position: relative;
        flex-shrink: 0;

        /deep/ .right-panel-header {
          flex-shrink: 0;
          display: flex;
          align-items: center;
          height: 52px;
          line-height: 20px;
          background-color: #323232;
          color: #dcdee5;
          border-left: 1px solid $newBlackColor2;
          font-size: 12px;
          box-shadow: 0 2px 4px 0 rgba(0, 0, 0, .3);
          z-index: 1;

          .icon-container {
            flex-shrink: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            width: 46px;
            height: 100%;
            background: #346;
            cursor: pointer;

            .icon-expand-line {
              font-size: 18px;
              color: #c4c6cc;
              transition: color .2s;
            }

            &:hover .icon-expand-line {
              color: #fff;
              transition: color .2s;
            }
          }

          .title {
            flex-shrink: 0;
            padding-left: 16px;
            font-size: 14px;
          }
        }

        /deep/ .right-panel-main {
          border-left: 1px solid #383838;
        }
      }
    }

    .code-footer {
      flex-shrink: 0;
      display: flex;
      align-items: center;
      height: 50px;
      margin: 0 60px;
      padding-left: 47px;
      background: #323232;
      box-shadow: 0 -2px 4px 0 rgba(0, 0, 0, .3);
      z-index: 1;

      .king-button {
        position: relative;
        margin-right: 10px;
        min-width: 86px;

        &.is-draft-updated::after {
          position: absolute;
          top: -3px;
          right: -3px;
          content: '';
          display: block;
          width: 6px;
          height: 6px;
          background-color: #c53333;
          border-radius: 3px;
        }
      }
    }
  }
</style>

<style lang="postcss">
  .tippy-tooltip.black-arrow-theme {
    .tippy-arrow {
      border-top-color: #000;
      border-bottom-color: #000;
    }
  }
</style>
