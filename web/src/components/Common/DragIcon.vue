<template>
  <div :class="['drag-icon', placement]" @mousedown.left="$emit('dragBegin', $event, prop)">
    <span class="dot"></span>
    <span class="dot"></span>
    <span class="dot"></span>
    <span class="dot"></span>
  </div>
</template>

<script>
export default {
  props: {
    prop: {
      type: String,
      default: 'default',
    },
    placement: {
      type: String,
      default: 'left',
    },
  },
};
</script>

<style scoped lang="postcss">
  @import '../../css/variable.css';

  .drag-icon {
    position: absolute;
    justify-content: space-between;
    display: flex;
    z-index: 10;
    cursor: move;
    &.left {
      flex-flow: column;
      top: 50%;
      left: 0;
      width: 9px;
      height: 36px;
      padding: 9px 3px;
      transform: translateY(-50%);
    }

    &.top {
      width: 36px;
      height: 9px;
      left: 50%;
      top: 0;
      padding: 3px 9px;
      transform: translateX(-50%);
    }

    .dot {
      width: 3px;
      height: 3px;
      border-radius: 50%;
      background: $newBlackColor2;
      transition: background-color .3s;
    }

    &:hover,
    &.active {
      .dot {
        background: #dcdee5;
        transition: background-color .3s;
      }
    }
  }
</style>
