<template>
  <bk-dialog
    :value="show"
    :mask-close="false"
    :position="{ top: dialogTop }"
    width="1200"
    ext-cls="cover-draft-dialog"
    @value-change="handleValueChange">
    <div slot="header" class="header-container">
      <div>{{ $t('当前已有草稿，是否覆盖？') }}</div>
      <DiffNav :diff-count="diffCount" @previous="jumpPreviousChange" @next="jumpNextChange" />
    </div>
    <div class="content-container">
      <template v-if="showEditor">
        <div class="cover-dialog-title">
          <div class="cover-dialog-title-half">
            #{{ draftVersion.config_version_id + ' ' + draftVersion.description }}
            <TagDraft dark />
          </div>
          <div class="cover-dialog-title-half">
            #{{ coverVersion.config_version_id + ' ' + coverVersion.description }}
            <TagAvailable v-if="coverVersion.is_active" dark />
          </div>
        </div>
        <DiffEditor ref="diffEditorRef" style="height: calc(100% - 52px);"
                    :old-data="oldData" :new-data="newData" :diff-count.sync="diffCount" />
      </template>
    </div>
    <div slot="footer" class="footer-container">
      <bk-button v-test="'cover'" class="confirm-button" theme="primary" :loading="loading" @click="handleConfirm">
        {{ $t('确定覆盖') }}
      </bk-button>
      <bk-button @click="handleCancel">{{ $t('取消') }}</bk-button>
    </div>
  </bk-dialog>
</template>

<script>
import TagDraft from '../TagDraft';
import TagAvailable from '../TagAvailable';
import DiffNav from '@/components/DiffNav';
import DiffEditor from '@/components/DiffEditor';
import dialogTopMixin from '@/mixins/dialogTop';

export default {
  components: {
    TagDraft,
    TagAvailable,
    DiffNav,
    DiffEditor,
  },
  mixins: [dialogTopMixin],
  props: {
    show: {
      type: Boolean,
      default: false,
    },
    versionList: {
      type: Array,
      required: true,
    },
    coverVersion: {
      type: Object,
      default: null,
    },
  },
  data() {
    return {
      dialogHeight: 620, // 弹窗高度
      showEditor: false,
      loading: false,
      diffCount: 0,
      draftVersion: null,
      oldData: {
        content: '',
        language: 'python',
      },
      newData: {
        content: '',
        language: 'python',
      },
    };
  },
  watch: {
    show(val) {
      if (val) {
        const draftVersion = this.versionList.find(item => item.is_draft);
        this.draftVersion = draftVersion;
        this.oldData = {
          content: draftVersion.content,
          language: draftVersion.file_format,
        };
        this.newData = {
          content: this.coverVersion.content,
          language: this.coverVersion.file_format,
        };
        setTimeout(() => {
          this.showEditor = true;
        });
      } else {
        this.showEditor = false;
      }
    },
  },
  methods: {
    handleValueChange(val) {
      this.$emit('update:show', val);
    },
    jumpNextChange() {
      this.$refs.diffEditorRef.diffNavigator.next();
    },
    jumpPreviousChange() {
      this.$refs.diffEditorRef.diffNavigator.previous();
    },
    async handleConfirm() {
      try {
        this.loading = true;
        const versionId = this.draftVersion.config_version_id;
        const res = await this.$store.dispatch('configVersion/ajaxUpdateConfigVersion', {
          versionId,
          data: {
            description: this.coverVersion.description,
            content: this.coverVersion.content,
            file_format: this.coverVersion.file_format,
            is_active: false,
            is_draft: true, // 覆盖草稿
          },
        });
        this.messageSuccess(this.$t('成功覆盖已有草稿'));
        this.$emit('coverSuccess', versionId, res.data);
      } catch (e) {
        console.warn(e);
      } finally {
        this.loading = false;
      }
    },
    handleCancel() {
      this.$emit('close');
    },
  },
};
</script>

<style scoped lang="postcss">
  @import '../../../../../css/variable.css';

  .header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 60px;
    padding-right: 20px;
    margin: -28px 0 1px;
    font-size: 20px;
    color: $newBlackColor1;
  }

  .content-container {
    height: 500px;

    .cover-dialog-title {
      display: flex;
      height: 52px;
      font-size: 12px;
      line-height: 16px;
      color: #c4c6cc;
      background: #323232;

      .cover-dialog-title-half {
        display: flex;
        align-items: center;
        width: calc(50% - 15px);
        padding-left: 18px;

        &:first-child {
          border-right: 1px solid $newBlackColor2;
        }
      }
    }
  }

  .footer-container {
    display: flex;
    justify-content: flex-end;
    align-items: center;

    .confirm-button {
      min-width: 120px;
      margin-right: 10px;
    }
  }
</style>

<style lang="postcss">
  .bk-dialog-wrapper.cover-draft-dialog {
    .bk-dialog-header,
    .bk-dialog-body {
      padding: 0 24px;
    }
  }
</style>
