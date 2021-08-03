<template>
  <div class="create-template-step2">
    <div class="title">{{ $t('基本信息') }}</div>
    <bk-form class="king-form" ref="form" :label-width="350" :model="formData" :rules="rules">
      <bk-form-item :label="$t('模板名称')" required property="template_name" error-display-type="normal">
        <bk-input v-model="formData.template_name" :clearable="true" :placeholder="$t('模板唯一标识')"></bk-input>
      </bk-form-item>
      <bk-form-item :label="$t('文件名称')" required property="file_name" error-display-type="normal">
        <bk-input v-model="formData.file_name" :clearable="true" :placeholder="$t('模板渲染生成的文件名称')"></bk-input>
      </bk-form-item>
      <bk-form-item :label="$t('文件绝对路径')" required property="abs_path" error-display-type="normal">
        <bk-input v-model="formData.abs_path" :clearable="true" :placeholder="$t('文件分发到服务器的路径')"></bk-input>
      </bk-form-item>
      <bk-form-item :label="$t('文件拥有者')" required property="owner" error-display-type="normal">
        <bk-input v-model="formData.owner" :clearable="true" :placeholder="$t('拥有者名称，操作系统必须存在此用户')"></bk-input>
      </bk-form-item>
      <bk-form-item :label="$t('文件用户组')" required property="group" error-display-type="normal">
        <bk-input v-model="formData.group" :clearable="true" :placeholder="$t('用户组名称，操作系统必须存在此用户组')"></bk-input>
      </bk-form-item>
      <bk-form-item :label="$t('文件权限')" required property="filemode" error-display-type="normal">
        <bk-input v-model="formData.filemode" :clearable="true" :placeholder="$t('文件的权限设置，如0775')"></bk-input>
      </bk-form-item>
      <bk-form-item :label="$t('输出格式')" required property="line_separator" error-display-type="normal">
        <bk-select v-model="formData.line_separator" :clearable="true" :placeholder="$t('请选择文件输出格式')">
          <bk-option id="CRLF" name="CRLF - Windows（\r\n）"></bk-option>
          <bk-option id="LF" name="LF - Unix and macOS（\n）"></bk-option>
        </bk-select>
      </bk-form-item>
    </bk-form>
  </div>
</template>

<script>
export default {
  props: {},
  data() {
    const required = {
      required: true,
      message: window.i18n.t('必填项'),
      trigger: 'blur',
    };
    return {
      formData: {
        bk_biz_id: this.$store.state.bizId,
        template_name: '',
        file_name: '',
        abs_path: '',
        owner: '',
        group: '',
        filemode: '0775',
        line_separator: 'LF',
      },
      rules: {
        template_name: [required],
        file_name: [required],
        abs_path: [required, {
          validator: val => val.match(/^\/|^[a-zA-Z]:[\\]/),
          message: this.$t('路径格式非法，请检查绝对路径格式是否正确'),
          trigger: 'blur',
        }],
        owner: [required, {
          validator: val => val.match(/^[a-zA-Z][a-zA-Z0-9]*$/),
          message: this.$t('请输入英文字母或数字，且必须以英文字母开头'),
          trigger: 'blur',
        }],
        group: [required, {
          validator: val => val.match(/^[a-zA-Z][a-zA-Z0-9]*$/),
          message: this.$t('请输入英文字母或数字，且必须以英文字母开头'),
          trigger: 'blur',
        }],
        filemode: [required, {
          validator: val => val.match(/^[0-7]{4}$/),
          message: this.$t('文件权限设置提示'),
          trigger: 'blur',
        }],
        line_separator: [required],
      },
    };
  },
  methods: {},
};
</script>

<style scoped lang="postcss">
  @import '../../../../../css/variable.css';

  .create-template-step2 {
    position: relative;
    display: flow-root;
    height: 502px;
    overflow: auto;

    .title {
      position: absolute;
      top: 40px;
      right: 666px;
      font-size: 16px;
      color: $newBlackColor1;
    }

    .king-form {
      margin-top: 81px;

      /deep/ .bk-form-control,
      .bk-select {
        width: 380px;
      }

      /deep/ .bk-form-content {
        position: relative;

        .form-error-tip {
          position: absolute;
          top: 100%;
          margin: 0;
        }
      }
    }
  }
</style>
