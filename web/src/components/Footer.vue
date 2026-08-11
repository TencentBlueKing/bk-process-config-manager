<template>
  <div v-if="footerContent" class="footer-content">
    <!-- <div class="link-container">
      <template v-for="(item, index) in footerContent.footer">
        <a class="footer-link" :key="index" :href="item.link" :target="item.is_blank ? '_blank' : '_self'">
          {{ item.text }}
        </a>
        <span v-if="index !== footerContent.footer.length - 1" :key="index + 'gap'" class="gap"> | </span>
      </template>
    </div>
    <div>{{ footerContent.copyright }}</div> -->
    <p
      class="link-container"
      v-html="contact"
    ></p>
    <p class="copyright">{{copyright}}</p>
  </div>
</template>

<script>
export default {
  computed: {
    footerContent() {
      return this.$store.state.meta.footerContent;
    },
    contact() {
      return this.$store.state.platform.i18n.footerInfoHTML
    },
    copyright() {
      return this.$store.state.platform.footerCopyrightContent
    }
  },
};
</script>

<style lang="postcss" scoped>
  .footer-content {
    position: absolute;
    bottom: 0;
    right: 50vw;
    transform: translateX(50%);
    height: 50px;
    padding-top: 5px;
    display: flex;
    flex-flow: column;
    align-items: center;
    width: 100%;
    line-height: 20px;
    font-size: 12px;

    .link-container {
      display: flex;
      align-items: center;
      height: 20px;

      .footer-link {
        color: #3a84ff;

        &:hover {
          color: #699df4;
        }

        &:active {
          color: #2761dd;
        }
      }

      .gap {
        margin: -2px 4px 0 4px;
      }
    }
  }
</style>
