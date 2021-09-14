<template>
  <div class="draft-diff-container">
    <div class="draft-diff-header">
      <DiffNav :diff-count="diffCount" @previous="jumpPreviousChange" @next="jumpNextChange" />
    </div>
    <div class="draft-diff-title">
      <div class="draft-diff-title-half">
        <div class="status-flag">{{ $t('选择对比') }}</div>
        <bk-select
          v-model="selectedVersionId"
          ref="versionSelectRef"
          class="king-select dark"
          ext-popover-cls="dark"
          :clearable="false">
          <div slot="trigger" class="bk-select-name">
            <span v-bk-overflow-tips="{ distance: 20 }" class="text-overflow-row">
              #{{ compareVersion.config_version_id }} {{ compareVersion.description }}
            </span>
            <TagAvailable v-if="compareVersion.is_active" dark />
          </div>
          <template v-for="option in filterVersionList">
            <bk-option :key="option.config_version_id" :id="option.config_version_id" :name="option.description">
              <div style="display: flex;align-items: center">
                <span v-bk-overflow-tips="{ placement: 'right' }" class="text-overflow-row">
                  #{{ option.config_version_id + option.description }}
                </span>
                <TagAvailable v-if="option.is_active" dark />
              </div>
            </bk-option>
          </template>
        </bk-select>
      </div>
      <div class="draft-diff-title-half">
        <div class="status-flag">{{ $t('当前草稿') }}</div>
        <span v-bk-overflow-tips class="description-name text-overflow-row">
          #{{ draftVersion.config_version_id + ' ' + draftVersion.description }}
        </span>
        <TagDraft dark />
      </div>
    </div>
    <div class="diff-editor-content">
      <DiffEditor
        v-if="showDiffEditor"
        ref="diffEditorRef"
        :old-data="oldData"
        :new-data="newData"
        :diff-count.sync="diffCount" />
    </div>
    <div class="diff-editor-footer">
      <bk-button :loading="isLoading" @click="coverDraftWithSelected">{{ $t('用对比版本覆盖当前草稿') }}</bk-button>
      <bk-button style="margin-left: 10px;">{{ $t('取消') }}</bk-button>
    </div>
  </div>
</template>

<script>
import TagAvailable from '../TagAvailable';
import TagDraft from '../TagDraft';
import DiffNav from '@/components/DiffNav';
import DiffEditor from '@/components/DiffEditor';

export default {
  components: {
    TagAvailable,
    TagDraft,
    DiffNav,
    DiffEditor,
  },
  props: {
    versionList: {
      type: Array,
      required: true,
    },
    draftVersion: {
      type: Object,
      required: true,
    },
    newData: {
      type: Object,
      default() {
        return {
          content: '',
          language: 'python',
        };
      },
    },
  },
  data() {
    const filterVersionList = this.versionList.filter(item => !item.is_draft);
    const compareVersion = filterVersionList[0];
    const selectedVersionId = compareVersion.config_version_id;
    return {
      selectedVersionId,
      compareVersion,
      filterVersionList,
      showDiffEditor: true,
      isLoading: false,
      diffCount: 0,
    };
  },
  computed: {
    oldData() {
      return {
        content: this.compareVersion.content,
        language: this.compareVersion.file_format || 'python',
      };
    },
  },
  watch: {
    selectedVersionId(val) {
      this.compareVersion = this.filterVersionList.find(item => item.config_version_id === val);
      this.showDiffEditor = false;
      this.$nextTick(() => {
        this.showDiffEditor = true;
      });
    },
  },
  methods: {
    jumpNextChange() {
      this.$refs.diffEditorRef.diffNavigator.next();
    },
    jumpPreviousChange() {
      this.$refs.diffEditorRef.diffNavigator.previous();
    },
    async coverDraftWithSelected() {
      try {
        this.isLoading = true;
        const versionId = this.draftVersion.config_version_id;
        const res = await this.$store.dispatch('configVersion/ajaxUpdateConfigVersion', {
          versionId,
          data: {
            description: this.compareVersion.description,
            content: this.compareVersion.content,
            file_format: this.compareVersion.file_format,
            is_active: false,
            is_draft: true, // 覆盖草稿
          },
        });
        this.$emit('coverSuccess', res);
      } catch (e) {
        console.warn(e);
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>

<style scoped lang="postcss">
  @import '../../../../../css/variable.css';

  .draft-diff-container {
    display: flex;
    flex-direction: column;
    height: calc(100vh - 60px);

    .draft-diff-header {
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: flex-end;
      height: 56px;
      padding-right: 30px;
    }

    .draft-diff-title {
      z-index: 1;
      flex-shrink: 0;
      display: flex;
      height: 52px;
      margin: 0 30px;
      font-size: 14px;
      line-height: 16px;
      color: #c4c6cc;
      background: #323232;
      box-shadow: 0 2px 4px 0 rgba(0, 0, 0, .3);

      .draft-diff-title-half {
        display: flex;
        align-items: center;
        width: calc(50% - 15px);

        &:first-child {
          border-right: 1px solid $newBlackColor2;
        }

        .king-select {
          margin: 0 20px;
          min-width: 320px;
        }

        .bk-select-name {
          display: flex;
          align-items: center;
          font-size: 14px;
          overflow: hidden;
        }
      }

      .status-flag {
        flex-shrink: 0;
        padding: 0 10px;
        text-align: center;
        min-width: 60px;
        line-height: 52px;
        color: $newBlackColor3;
        background: #424242;
      }

      .description-name {
        padding-left: 20px;
        line-height: 52px;
        color: #c4c6cc;
      }
    }

    .diff-editor-content {
      height: calc(100% - 138px);
      margin: 0 30px;
    }

    .diff-editor-footer {
      flex-shrink: 0;
      display: flex;
      margin: 10px 30px 10px;
    }
  }
</style>
