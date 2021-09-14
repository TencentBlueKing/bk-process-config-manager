<template>
  <div class="edit-wrapper">
    <div class="edit-content">
      <div class="edit-title">
        <i18n path="编辑范围Num"><span class="num">{{ selections.length }}</span></i18n>
      </div>
      <bk-form ext-cls="process-edit-form" ref="processEditForm" form-type="vertical" :model="propForm">
        <bk-form-item error-display-type="normal" property="selected" :label="$t('编辑字段')" required :rules="selectRule">
          <bk-tag-input
            has-delete-icon
            trigger="focus"
            :list="propList"
            :placeholder="$t('请选择')"
            v-model="propForm.selected">
          </bk-tag-input>
        </bk-form-item>
        <bk-form-item
          v-for="(prop, index) in propForm.selected"
          :key="index"
          required
          error-display-type="normal"
          :label="labelMap[prop]"
          :property="prop"
          :rules="requireRule">
          <div class="form-prop-item">
            <bk-input v-model="propForm[prop]"></bk-input>
            <i class="delete-icon ml10 gsekit-icon gsekit-icon-close-line" @click="handleEditDelete(index)"></i>
          </div>
        </bk-form-item>
        <bk-form-item class="mt30">
          <bk-button theme="primary" @click.stop.prevent="validateForm" :loading="isChecking">{{ $t('确定') }}</bk-button>
          <bk-button ext-cls="ml5" theme="default" @click.stop.prevent="cancelEdit">{{ $t('取消') }}</bk-button>
        </bk-form-item>
      </bk-form>
    </div>
    <div class="variable-content">
      <p class="title">{{ $t('全局变量') }}</p>
      <bk-table
        class="mt20"
        v-bkloading="{ isLoading: loading }"
        :empty-text="$t('暂无变量')"
        :data="tableData"
        :row-style="setRowStyle"
        :outer-border="false"
        @row-click="handleClickRow">
        <bk-table-column prop="name" width="134" :label="$t('名称')" v-bk-overflow-tips></bk-table-column>
        <bk-table-column prop="value" :label="$t('变量')">
          <template slot-scope="{ row, $index }">
            <bk-popover
              :ref="`valuePopover${$index}`"
              trigger="click"
              :content="$t('复制成功')">
              {{ row.value }}
            </bk-popover>
          </template>
        </bk-table-column>
      </bk-table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProcessSliderEdit',
  props: {
    selections: {
      type: Array,
      default: () => [],
    },
    propList: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      loading: false,
      isChecking: false,
      propForm: {},
      tableData: [],
      requireRule: [
        {
          required: true,
          message: this.$t('必填项'),
          trigger: 'blur',
        },
      ],
      selectRule: [
        {
          message: this.$t('必填项'),
          trigger: 'change',
          validator(val) {
            return val.length;
          },
        },
      ],
    };
  },
  computed: {
    labelMap() {
      return this.propList.map(item => ({ [item.id]: item.name })).reduce((obj, item) => Object.assign(obj, item), {});
    },
  },
  created() {
    this.setPropForm();
    this.getVariableList();
  },
  methods: {
    validateForm() {
      this.isChecking = true;
      this.$refs.processEditForm.validate().then(() => {
        this.isChecking = false;
      }, (validator) => {
        this.isChecking = false;
        console.warn(validator);
      });
    },
    cancelEdit() {
      this.$emit('cancel-edit');
    },
    getVariableList() {
      this.loading = true;
      const num = 100;
      const data = [];
      setTimeout(() => {
        for (let i = 1; i <= num; i++) {
          data.push({ name: `variable_${i}`, value: `$\{value_${i}}` });
        }
        this.tableData = data;
        this.loading = false;
      }, 1000);
    },
    handleClickRow(row, event, column, rowIndex) {
      const input = document.createElement('input');
      input.setAttribute('value', row.value);
      document.body.appendChild(input);
      input.select();
      const res = document.execCommand('copy');
      document.body.removeChild(input);
      if (res) {
        const popover = this.$refs[`valuePopover${rowIndex}`];
        popover.showHandler();
        setTimeout(() => {
          popover.hideHandler();
        }, 1000);
      }
    },
    handleEditDelete(index) {
      this.propForm.selected.splice(index, 1);
    },
    setPropForm() {
      const form = {
        selected: [],
      };
      this.propList.forEach((item) => {
        form[item.id] = '';
      });
      this.$set(this, 'propForm', form);
    },
    setRowStyle() {
      return { cursor: 'pointer' };
    },
  },
};
</script>

<style lang="postcss" scoped>
  .edit-wrapper {
    display: flex;
    height: 100%;
    overflow: hidden;

    .edit-content {
      padding: 20px 30px;
      width: 450px;
      background: #f5f6fa;
      overflow: auto;

      .edit-title {
        margin: 0 0 14px 0;
        font-size: 14px;
        color: #63656e;
      }

      .num {
        color: #3a84ff;
      }
    }

    .process-edit-form {
      .form-prop-item {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .delete-icon:hover {
          color: #3a84ff;
        }
      }

      .bk-form-item + .bk-form-item {
        margin-top: 10px;
      }
    }

    .variable-content {
      flex: 1;
      padding: 18px 20px;
      overflow: auto;
    }
  }
</style>
