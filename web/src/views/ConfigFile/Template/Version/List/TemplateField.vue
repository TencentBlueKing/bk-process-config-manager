<template>
  <div class="field-content">
    <span class="field-text">{{ fieldText }}</span>
    <template v-if="isEdit">
      <bk-select
        v-if="field === 'line_separator'"
        v-model.trim="initialValue"
        @toggle="handleSelectToggle"
        ref="select"
        style="width: 260px;"
        :clearable="false">
        <bk-option id="CRLF" name="CRLF - Windows（\r\n）"></bk-option>
        <bk-option id="LF" name="LF - Unix and macOS（\n）"></bk-option>
      </bk-select>
      <bk-input
        v-else
        v-model.trim="initialValue"
        v-bk-clickoutside="handleChange"
        @enter="handleChange"
        ref="input"
        style="width: 260px;"
      ></bk-input>
    </template>
    <template v-else>
      <span v-if="field === 'line_separator'" class="field-value">
        {{ lineSeparatorMap[selectedConfig[field]] || '--' }}
      </span>
      <span v-else class="field-value" v-bk-overflow-tips>{{ selectedConfig[field] || '--' }}</span>
      <svg v-if="isLoading" class="svg-icon" aria-hidden="true">
        <use xlink:href="#gsekit-icon-loading"></use>
      </svg>
      <AuthTag
        v-else
        class="gsekit-icon gsekit-icon-edit-fill"
        action="edit_config_template"
        :id="selectedConfig.config_template_id"
        :authorized="selectedConfig.edit_config_template"
        @click="editField">
      </AuthTag>
    </template>
  </div>
</template>

<script>
export default {
  props: {
    selectedConfig: {
      type: Object,
      default() {
        return {};
      },
    },
    field: {
      type: String,
      default: '',
    },
    fieldText: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      initialValue: this.selectedConfig[this.field],
      isEdit: false,
      isLoading: false,
      lineSeparatorMap: {
        LF: 'LF - Unix and macOS（\\n）',
        CRLF: 'CRLF - Windows（\\r\\n）',
      },
      rules: {
        abs_path: {
          validator: val => val.match(/^\/|^[a-zA-Z]:[\\]/),
          message: this.$t('路径格式非法，请检查绝对路径格式是否正确'),
        },
        owner: {
          validator: val => val.match(/^[a-zA-Z][a-zA-Z0-9]*$/),
          message: this.$t('请输入英文字母或数字，且必须以英文字母开头'),
        },
        group: {
          validator: val => val.match(/^[a-zA-Z][a-zA-Z0-9]*$/),
          message: this.$t('请输入英文字母或数字，且必须以英文字母开头'),
        },
        filemode: {
          validator: val => val.match(/^[0-7]{4}$/),
          message: this.$t('文件权限设置提示'),
        },
      },
    };
  },
  methods: {
    editField() {
      this.isEdit = true;
      this.$nextTick(this.focusOnForm);
    },
    focusOnForm() {
      if (this.field === 'line_separator') { // 下拉表单
        const selectTrigger = this.$refs.select.$el.querySelector('.bk-select-name');
        selectTrigger.click();
      } else {
        this.$refs.input.$el.querySelector('input').select();
      }
    },
    handleSelectToggle(val) {
      if (!val) { // 关闭即修改
        this.handleChange();
      }
    },
    async handleChange() {
      // 规则校验
      const val = this.initialValue;
      const rule = this.rules[this.field];
      if (rule) {
        if (!rule.validator(val)) {
          this.messageError(rule.message);
          this.focusOnForm();
          return;
        }
      }
      this.isEdit = false;
      // 是否做出了修改
      if (val === this.selectedConfig[this.field]) {
        return;
      }
      // 修改字段数据
      try {
        this.isLoading = true;
        await this.$store.dispatch('configTemplate/ajaxUpdateConfigTemplate', {
          templateId: this.$route.params.templateId,
          data: {
            [this.field]: val,
          },
        });
        this.$set(this.selectedConfig, this.field, this.initialValue);
        this.messageSuccess(this.$t('修改成功'));
      } catch (e) {
        this.initialValue = this.selectedConfig[this.field];
        console.warn(e);
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>
