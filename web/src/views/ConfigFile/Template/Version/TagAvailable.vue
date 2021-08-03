<template>
  <span :style="style">
    {{ $t('可用') }}
  </span>
</template>

<script>
export default {
  props: {
    dark: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      style: {
        'flex-shrink': '0',
        padding: '0 4px',
        'margin-left': '4px',
        'font-size': '12px',
        'line-height': '16px',
        color: this.dark ? '#59B383' : '#3FC06D',
        background: this.dark ? '#1F4D28' : '#E5F6EA',
        'border-radius': '2px',
      },
    };
  },
};
</script>
