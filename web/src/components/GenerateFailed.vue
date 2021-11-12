<template>
  <div class="generate-fail">
    <bk-popover ext-cls="failed-tips" placement="bottom" theme="light" :max-width="500" :always="false">
      <StatusView :type="statusType" :text="text" />
      <template slot="content">
        <div class="failed-message">
          <div class="message-text">{{ '失败信息：' }}</div>
          <!-- eslint-disable-next-line vue/no-v-html -->
          <div v-html="failedReason || '--'"></div>
        </div>
        <div class="resolve-message" v-if="solutions && solutions.length">
          <div class="message-text">{{ '解决方案：' }}</div>
          <div v-for="(soluteItem, index) in solutions" :key="index">
            <div class="solute-item">
              <span class="solute-item-order">{{ index + 1 + '.' }}</span>
              <!-- eslint-disable-next-line vue/no-v-html -->
              <div class="solute-item-content" v-html="soluteItem.html"></div>
            </div>
          </div>
        </div>
      </template>
    </bk-popover>
  </div>
</template>
<script>
export default {
  props: {
    statusType: {
      type: String,
      default: 'failed',
    },
    text: {
      type: String,
      default() {
        return this.$t('执行失败');
      },
    },
    failedReason: {
      type: String,
      default: '',
    },
    solutions: {
      type: Array,
      default() {
        return [];
      },
    },
  },
};
</script>
<style lang="postcss" scoped>
  .generate-fail {
    cursor: default;

    /deep/ .loading-text {
      line-height: 18px;
      border-bottom: 1px dashed #c4c6cc;
    }
  }
</style>
