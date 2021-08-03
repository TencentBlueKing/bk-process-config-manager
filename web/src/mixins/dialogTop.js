export default {
  data() {
    return {
      dialogTop: 72,
    };
  },
  mounted() {
    this.handleResize();
    window.addEventListener('resize', this.handleResize);
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.handleResize);
  },
  methods: {
    handleResize() {
      try {
        const top = (window.innerHeight - this.dialogHeight) / 2;
        this.dialogTop = top < 72 ? 72 : top;
      } catch (e) {
        console.warn(e);
        this.dialogTop = 72;
      }
    },
  },
};
