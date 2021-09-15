<template>
  <div class="create-template-step2">
    <div class="title">{{ $t('基本信息') }}</div>
    <bk-form class="king-form" v-test="'tempForm'" ref="form" :label-width="350" :model="formData" :rules="rules">
      <template v-for="item in formItems">
        <bk-form-item
          error-display-type="normal"
          :key="item.prop"
          :label="item.label"
          :required="item.required"
          :property="item.prop">
          <bk-select
            v-if="item.type === 'select'"
            v-test="'tempSelect'"
            :test-key="item.prop"
            v-model="formData[item.prop]"
            :clearable="true"
            :placeholder="item.placeholder">
            <bk-option v-for="option in item.options" :key="option.id" :id="option.id" :name="option.name" />
          </bk-select>
          <bk-input
            v-else
            v-test="'tempInput'"
            :test-key="item.prop"
            :clearable="item.clearable"
            v-model="formData[item.prop]"
            :placeholder="item.placeholder">
          </bk-input>
        </bk-form-item>
      </template>
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
      formItems: [
        { label: this.$t('模板名称'), required: true, prop: 'template_name', clearable: true, placeholder: this.$t('模板唯一标识') },
        { label: this.$t('文件名称'), required: true, prop: 'file_name', clearable: true, placeholder: this.$t('模板渲染生成的文件名称') },
        { label: this.$t('文件所处路径'), required: true, prop: 'abs_path', clearable: true, placeholder: this.$t('文件分发到服务器的路径') },
        { label: this.$t('文件拥有者'), required: true, prop: 'owner', clearable: true, placeholder: this.$t('拥有者名称，操作系统必须存在此用户') },
        { label: this.$t('文件用户组'), required: true, prop: 'group', clearable: true, placeholder: this.$t('用户组名称，操作系统必须存在此用户组') },
        { label: this.$t('文件权限'), required: true, prop: 'filemode', clearable: true, placeholder: this.$t('文件的权限设置，如0775') },
        {
          label: this.$t('输出格式'),
          required: true,
          prop: 'line_separator',
          clearable: true,
          placeholder: this.$t('请选择文件输出格式'),
          type: 'select',
          options: [
            { id: 'CRLF', name: 'CRLF - Windows（\\r\\n）' },
            { id: 'LF', name: 'LF - Unix and macOS（\\n）' },
          ],
        },
      ],
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
