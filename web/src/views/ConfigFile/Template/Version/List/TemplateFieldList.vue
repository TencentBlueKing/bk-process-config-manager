<template>
  <div class="template-field-list-container">
    <div class="row">
      <div class="couple">
        <TemplateField :selected-config="selectedConfig" field="template_name" :field-text="$t('模板名称') + $t('：')" />
      </div>
      <div class="couple">
        <TemplateField :selected-config="selectedConfig" field="abs_path" :field-text="$t('文件所处路径') + $t('：')" />
      </div>
      <div class="couple">
        <TemplateField :selected-config="selectedConfig" field="owner" :field-text="$t('文件拥有者') + $t('：')" />
      </div>
      <div class="couple">
        <TemplateField :selected-config="selectedConfig" field="line_separator" :field-text="$t('输出格式') + $t('：')" />
      </div>
    </div>
    <div class="row">
      <div class="couple">
        <TemplateField :selected-config="selectedConfig" field="file_name" :field-text="$t('文件名称') + $t('：')" />
      </div>
      <div class="couple">
        <TemplateField :selected-config="selectedConfig" field="filemode" :field-text="$t('文件权限') + $t('：')" />
      </div>
      <div class="couple">
        <TemplateField :selected-config="selectedConfig" field="group" :field-text="$t('文件用户组') + $t('：')" />
      </div>
      <div class="couple">
        <div class="field-content">
          <span class="field-text">{{ $t('关联进程') + $t('：') }}</span>
          <span v-if="selectedConfig.relation_count" class="field-value button-text" @click="showBindProcess = true">
            {{ selectedConfig.relation_count.TEMPLATE + selectedConfig.relation_count.INSTANCE }}
          </span>
        </div>
      </div>
    </div>
    <BindProcessDialog
      :template-item="selectedConfig"
      :show-dialog.sync="showBindProcess"
      @bindSuccess="handleBindSuccess" />
  </div>
</template>

<script>
import TemplateField from './TemplateField';
import BindProcessDialog from '@/views/ConfigFile/Template/List/BindProcess/Dialog';

export default {
  components: {
    TemplateField,
    BindProcessDialog,
  },
  props: {
    selectedConfig: {
      type: Object,
      default() {
        return {};
      },
    },
  },
  data() {
    return {
      showBindProcess: false,
    };
  },
  methods: {
    handleBindSuccess(templateCount, instanceCount) {
      this.$emit('change', { key: 'relation_count', value: { TEMPLATE: templateCount, INSTANCE: instanceCount } });
      this.$emit('change', { key: 'is_bound', value: !!templateCount || !!instanceCount });
    },
  },
};
</script>

<style scoped lang="postcss">
  @import '../../../../../css/variable.css';

  .template-field-list-container {
    padding: 9px 60px;

    .row {
      display: flex;

      .couple {
        display: flex;
        width: 260px;
        height: 32px;
        padding-right: 16px;

        /deep/ .field-content {
          display: flex;
          align-items: center;
          font-size: 12px;
          line-height: 16px;
          max-width: 100%;
          color: $newBlackColor2;
          white-space: pre;

          &:hover .gsekit-icon-edit-fill {
            display: block;
          }

          .field-text {
            flex-shrink: 0;
            color: #b2b5bd;
          }

          .field-value {
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }

          .gsekit-icon-edit-fill {
            flex-shrink: 0;
            display: none;
            margin-left: 8px;
            color: #c4c6cc;
            font-size: 16px;
            cursor: pointer;

            &:not(.auth-box-disabled):hover {
              color: $newMainColor;
            }
          }

          .svg-icon {
            margin-left: 8px;
            width: 16px;
            height: 16px;
          }
        }
      }
    }
  }
</style>
