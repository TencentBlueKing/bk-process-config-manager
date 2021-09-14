<template>
  <div class="expand-th-container">
    <span
      v-if="column.tips"
      class="text-has-tips"
      v-bk-tooltips="{
        content: column.tips,
        placement: tipsPlacement
      }">{{ column.label }}</span>
    <span v-else>{{ column.label }}</span>
    <div
      class="expand-btn"
      v-bk-tooltips="{
        content: isExpand ? $t('收起配置字段') : $t('展开配置字段'),
        placement: 'right'
      }"
      @click.stop="handleToggleExpand">
      <i :class="`gsekit-icon gsekit-icon-${ isExpand ? 'shouqi' : 'zhankai'}`"></i>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ExpandTh',
  props: {
    column: {
      type: Object,
      default: () => ({}),
    },
    isExpand: {
      type: Boolean,
      default: false,
    },
    tipsPlacement: {
      type: String,
      default: 'top',
    },
  },
  methods: {
    handleToggleExpand() {
      this.$emit('click-expand', !this.column.isExpand);
    },
  },
};
</script>

<style lang="postcss" scoped>
  .expand-th-container {
    position: relative;

    .expand-btn {
      position: absolute;
      left: 50%;
      bottom: -7px;
      display: flex;
      justify-content: center;
      font-size: 13px;
      color: #c4c6cc;
      cursor: pointer;
      transform: translateX(-50%);

      &:hover {
        color: #3a84ff;
      }
    }
  }
</style>
