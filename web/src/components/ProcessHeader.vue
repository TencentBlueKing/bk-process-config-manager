<template>
  <section>
    <div class="process-header">
      <bk-popover :content="tips" :max-width="200">
        <span>{{ name }}</span>
      </bk-popover>
    </div>
  </section>
</template>
<script>
export default {
  name: 'ProcessHeader',
  props: {
    name: {
      type: String,
      default: '',
    },
    tips: {
      type: String,
      default: '',
    },
  },
};
</script>
<style lang="postcss" scoped>
  /deep/ .bk-tooltip-ref {
    line-height: 24px;
  }

  .process-header {
    cursor: pointer;

    span {
      border-bottom: 1px dashed #c4c6cc;
      padding-bottom: 3px;
      min-width: 60px;
    }
  }
</style>
