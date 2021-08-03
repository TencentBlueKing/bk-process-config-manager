<template>
  <span :style="style">
    {{ $t('草稿') }}
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
        color: this.dark ? '#80AAFF' : '#3A84FF',
        background: this.dark ? '#293D66' : '#E1ECFF',
        'border-radius': '2px',
      },
    };
  },
};
</script>
