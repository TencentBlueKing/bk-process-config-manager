<template>
  <div class="diff-nav-container">
    <span>{{ $t('共') }} <span style="font-weight: bold">{{ diffCount }}</span> {{ $t('处差异') }}</span>
    <bk-button class="king-button" icon="icon-arrows-up" style="margin: 0 10px 0 26px;" @click="$emit('previous')">
    </bk-button>
    <bk-button class="king-button" icon="icon-arrows-down" @click="$emit('next')"></bk-button>
  </div>
</template>

<script>
export default {
  props: {
    diffCount: {
      type: Number,
      default: 0,
    },
  },
};
</script>

<style scoped lang="postcss">
  @import '../css/variable.css';

  .diff-nav-container {
    display: flex;
    align-items: center;
    font-size: 12px;
    color: $newBlackColor2;

    .king-button {
      padding: 0;

      /deep/ .bk-icon {
        top: 3px;
        color: $newBlackColor3;
        font-size: 28px;
      }
    }
  }
</style>
