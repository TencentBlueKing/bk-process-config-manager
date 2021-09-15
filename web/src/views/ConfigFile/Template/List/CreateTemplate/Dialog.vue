<template>
  <bk-dialog :value="showCreate"
             :mask-close="false"
             :close-icon="false"
             :position="{ top: dialogTop }"
             width="1000"
             ext-cls="create-template-dialog"
             header-position="left"
             @value-change="handleValueChange">
    <div slot="header" class="bk-dialog-header-inner">
      <template v-if="isFirstStep">
        {{ $t('新建配置文件模板') }}
      </template>
      <template v-else>
        {{ $t('关联进程') }}
        <span style="font-size: 14px;font-weight: bold;line-height: 62px;vertical-align: top;">{{ ' - ' }}</span>
        <span style="font-size: 18px;font-weight: normal;">
          {{ newTemplate.template_name + '(' + newTemplate.file_name + ')' }}
        </span>
      </template>
    </div>
    <template v-if="showCreate">
      <BasicInfo ref="basicInfo" v-show="isFirstStep" />
      <ProcessSelect ref="processSelect" v-show="!isFirstStep" />
    </template>
    <div slot="footer" class="footer-wrapper">
      <bk-button
        v-show="isFirstStep" v-test.common="'stepNext'" theme="primary" :loading="createLoading" @click="handleCreate">
        {{ $t('下一步') }}
      </bk-button>
      <bk-button v-show="isFirstStep" v-test.form="'cancel'" @click="handleCancel">
        {{ $t('取消') }}
      </bk-button>
      <bk-button
        v-show="!isFirstStep" v-test.form="'confirm'" theme="primary" :loading="bindLoading" @click="handleBind">
        {{ $t('关联') }}
      </bk-button>
      <bk-button v-show="!isFirstStep" v-test.form="'cancel'" @click="handleSkip">
        {{ $t('暂不关联') }}
      </bk-button>
    </div>
  </bk-dialog>
</template>

<script>
import BasicInfo from './BasicInfo';
import ProcessSelect from '../BindProcess/ProcessSelect';
import dialogTopMixin from '@/mixins/dialogTop';

export default {
  components: {
    BasicInfo,
    ProcessSelect,
  },
  mixins: [dialogTopMixin],
  props: {
    showCreate: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      dialogHeight: 618, // 弹窗高度
      isFirstStep: true,
      createLoading: false,
      newTemplate: {}, // 新建的配置模板
      bindLoading: false,
    };
  },
  methods: {
    handleValueChange(val) {
      this.$emit('update:showCreate', val);
      if (!val) { // 关闭时重置数据
        this.isFirstStep = true;
        this.createLoading = false;
        this.newTemplate = {};
        this.bindLoading = false;
      }
    },
    async handleCreate() {
      try {
        await this.$refs.basicInfo.$refs.form.validate();
        this.createLoading = true;
        const res = await this.$store.dispatch('configTemplate/ajaxCreateConfigTemplate', {
          data: this.$refs.basicInfo.formData,
        });
        res.data.config_template_id += '';
        this.newTemplate = res.data;
        this.isFirstStep = false;
        this.messageSuccess('配置文件模板，新建成功。');
      } catch (e) {
        console.warn(e);
      } finally {
        this.createLoading = false;
      }
    },
    handleCancel() {
      this.$emit('update:showCreate', false);
    },
    async handleBind() {
      try {
        this.bindLoading = true;
        const { templateProcess, instanceProcess } = this.$refs.processSelect;
        if (!templateProcess.length && !instanceProcess.length) {
          this.handleSkip();
          return;
        }
        const processObjectList = [];
        templateProcess.forEach((item) => {
          processObjectList.push({
            process_object_type: 'TEMPLATE',
            process_object_id: item.id,
          });
        });
        instanceProcess.forEach((item) => {
          processObjectList.push({
            process_object_type: 'INSTANCE',
            process_object_id: item.property.bk_process_id,
          });
        });
        const templateId = Number(this.newTemplate.config_template_id);
        await this.$store.dispatch('configTemplate/ajaxBindTemplateToProcess', {
          templateId,
          data: {
            process_object_list: processObjectList,
          },
        });
        this.messageSuccess(this.$t('关联成功'));
        this.$emit('created', this.newTemplate.config_template_id);
      } catch (e) {
        console.warn(e);
      } finally {
        this.bindLoading = false;
      }
    },
    // 确认是否要跳过绑定进程
    handleSkip() {
      this.$bkInfo({
        title: this.$t('请确认是否跳过关联进程'),
        subTitle: this.$t('该配置文件尚未关联进程'),
        confirmFn: () => this.$emit('created', this.newTemplate.config_template_id),
      });
    },
  },
};
</script>
