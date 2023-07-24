<template>
  <div>
    <div
      ref="dropdownDefaultRef"
      :class="isShow ? 'dropdown-active' : ''"
      @click="clickShow"
      v-bk-clickoutside="clickOutside">
      <slot />
    </div>
    <div v-show="false">
      <div ref="dropdownContentRef" class="bk-dropdown-content" @click="contentClick">
        <slot name="content" />
      </div>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    extCls: {
      type: String,
      default: '',
    },
    placement: {
      type: String,
      default: 'bottom',
    },
    theme: {
      type: String,
      default: 'nav-dropdown',
    },
    offset: {
      type: String,
      default: '0, 0',
    },
    arrow: {
      type: Boolean,
      default: false,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      isShow: false,
      trigger: 'mouseenter',
      popoverInstance: null,
      closeTimer: null,
    };
  },
  mounted() {
    this.updateInstance();
  },
  beforeDestroy() {
    this.popoverInstance && this.popoverInstance.destroy();
  },
  methods: {
    updateInstance() {
      this.popoverInstance = this.$bkPopover(this.$refs.dropdownDefaultRef, {
        content: this.$refs.dropdownContentRef,
        allowHTML: true,
        trigger: 'mouseenter',
        arrow: this.arrow,
        theme: `light bk-dropdown-popover ${this.theme}`,
        offset: this.offset,
        maxWidth: 274,
        sticky: true,
        duration: [275, 0],
        interactive: true,
        boundary: 'window',
        placement: 'top',
        hideOnClick: 'toggle',
        onHide: () => this.trigger === 'mouseenter',
        onTrigger: () => this.isShow = true,
        onHidden: () => this.isShow = false,
      });
    },
    clickShow() {
      if (this.popoverInstance) {
        this.trigger = 'manual';
        this.popoverInstance.show();
      }
    },
    clickOutside() {
      this.setTimer();
    },
    contentClick() {
      this.clearTimer();
      // 可增加 beforeClose 钩子
      this.setTimer();
    },
    hide() {
      this.trigger = 'mouseenter';
      this.popoverInstance && this.popoverInstance.hide();
    },
    setTimer() {
      this.closeTimer = window.setTimeout(this.hide, 50);
    },
    clearTimer() {
      if (this.closeTimer) {
        window.clearTimeout(this.closeTimer);
        this.closeTimer = null;
      }
    },
  },
};
</script>
