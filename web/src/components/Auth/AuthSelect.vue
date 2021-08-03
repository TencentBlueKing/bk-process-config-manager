<template>
  <bk-select
    ref="authBizSelect"
    ext-popover-cls="auth-extension"
    :value="selectValue"
    :placeholder="placeholder"
    :loading="loading"
    :ext-cls="extCls"
    :searchable="searchable"
    :multiple="multiple"
    :clearable="clearable"
    :readonly="readonly"
    :disabled="disabled"
    :popover-options="{ 'boundary': 'window' }"
    :popover-min-width="popoverMinWidth"
    @selected="handleSelected"
    @toggle="handleToggle"
    @change="handleChange"
    @clear="handleClear">
    <template v-for="item in optionList">
      <bk-option
        :key="item[id]"
        :id="item[id]"
        :name="item[name]"
        :class="{ 'is-auth-disabled': !item.view_business }"
        :disabled="item.disabled">
        <div class="bk-option-content-default" :title="item[name]">
          <span class="bk-option-name">
            {{ item[name] }}
          </span>
          <i
            class="select-item-icon bk-option-icon bk-icon icon-check-1"
            v-if="multiple && selectValue.includes(item[id])">
          </i>
          <AuthTag
            v-if="!item.view_business"
            class="bk-option-content-default"
            tag="div"
            type="biz"
            action="view_business"
            :auto-emit="true"
            :title="item[name]"
            :id="item.bk_biz_id"
            :authorized="item.view_business"
            @click="handleAuthClick(item)">
          </AuthTag>
        </div>
      </bk-option>
    </template>
    <div slot="extension" class="auth-extension-content" @click="handleExtension">
      <i class="bk-icon icon-plus-circle mr5"></i>{{ $t('新增') }}
    </div>
  </bk-select>
</template>
<script>
import { mapActions } from 'vuex';

export default {
  name: 'AuthSelect',
  model: {
    prop: 'value',
    event: 'update',
  },
  props: {
    value: {
      type: [String, Array, Number],
      default: '',
    },
    optionList: {
      type: Array,
      default: () => [],
    },
    // 外部样式
    extCls: {
      type: String,
      default: '',
    },
    placeholder: {
      type: String,
      default: '',
    },
    multiple: {
      type: Boolean,
      default: false,
    },
    searchable: {
      type: Boolean,
      default: false,
    },
    clearable: {
      type: Boolean,
      default: false,
    },
    readonly: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    id: {
      type: String,
      default: 'id',
    },
    name: {
      type: String,
      default: 'name',
    },
    // 权限动作
    action: {
      type: String,
      default: '',
    },
    // 权限类型
    type: {
      type: String,
      default: 'biz',
    },
    // extension slot
    extension: {
      type: Boolean,
      default: false,
    },
    // 权限控制
    permission: {
      type: [String, Boolean, Number],
      default: true,
    },
    popoverMinWidth: Number,
  },
  data() {
    return {
      loading: false, // select框加载
      selectValue: this.value,
    };
  },
  computed: {
    selectedItems() {
      if (this.selectValue instanceof Array) {
        return this.optionList.filter(item => this.selectValue.includes(item[this.id]) && item[this.action]);
      }
      return this.optionList.filter(item => this.selectValue === item[this.id] && item[this.action]);
    },
  },
  watch: {
    value(v) {
      this.selectValue = v;
    },
  },
  created() {
    this.handleInit();
  },
  methods: {
    ...mapActions('iam', ['ajaxGetAuthApplyInfo']),
    async handleInit() {
      // const copyValue = JSON.stringify(this.selectValue)
      // if (Array.isArray(this.selectValue)) {
      //     this.selectValue = this.optionList.filter(item => this.selectValue.includes(item[this.id])
      //         && (item.permission || item[this.action]))
      // } else {
      //     const option = this.optionList.find(item => this.selectValue === item[this.id]
      //         && (item.permission || item[this.action]))
      //     this.selectValue = option ? option[this.id] : ''
      // }
      // this.$emit('update', this.selectValue)
      // if (JSON.stringify(this.selectValue) !== copyValue) {
      //     this.$emit('change', this.selectValue, copyValue, this.selectedItems)
      // }
    },
    handleSelected(value, options) {
      this.$emit('selected', value, options, this.selectedItems);
    },
    handleToggle(toggle) {
      this.$emit('toggle', toggle, this.selectedItems);
    },
    handleChange(newValue, oldValue) {
      this.selectValue = newValue;
      this.$emit('update', newValue);
      this.$emit('change', newValue, oldValue, this.selectedItems);
    },
    handleClear(oldValue) {
      this.$emit('clear', oldValue, this.selectedItems);
    },
    handleAuthClick(option) {
      this.handleSelectClose();
      this.$emit('selected-auth', option);
    },
    handleSelectClose() {
      this.$refs.authBizSelect.close();
    },
    async handleExtension() {
      window.open(`${window.PROJECT_CONFIG.CMDB_URL}/#/resource/business`, '_blank');
    },
    show() {
      this.$refs.authBizSelect && this.$refs.authBizSelect.show();
    },
  },
};
</script>
<style lang="postcss" scoped>
  >>> .bk-select-loading {
    top: 6px;
  }

  .select {
    &-item {
      display: flex;

      &-name {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        margin-right: 4px;
      }

      &-id {
        color: #c4c6cc;
        margin-right: 20px;
      }

      >>> .bk-icon {
        top: 3px;
      }
    }
  }
</style>
