<template>
  <footer class="footer">
    <p class="footer-link" v-if="link.length">
      <span v-for="(item, index) in link" :key="index" class="footer-link-list">
        <a :href="item.href" :target="item.target" class="footer-link-item">
          {{ item.name }}
        </a>
      </span>
    </p>
    <p class="footer-copyright">
      {{ $t('蓝鲸版权', { year: new Date().getFullYear(), version: version }) }}
    </p>
  </footer>
</template>

<script>
export default {
  data() {
    return {
      link: [],
    };
  },
  created() {
    this.version =  window.PROJECT_CONFIG.VERSION;
    if (window.PROJECT_CONFIG.BKAPP_RUN_ENV === 'ieod') {
      this.link = [
        {
          name: window.i18n.t('联系BK助手'),
          href: window.PROJECT_CONFIG.BKAPP_NAV_HELPER_URL,
          target: '_blank',
        },
        {
          name: window.i18n.t('蓝鲸桌面'),
          href: window.PROJECT_CONFIG.DESTOP_URL,
          target: '_blank',
        },
      ];
    } else {
      this.link = [
        {
          name: window.i18n.t('技术支持'),
          href: window.PROJECT_CONFIG.BKAPP_NAV_HELPER_URL,
          target: '_blank',
        },
        {
          name: window.i18n.t('社区论坛'),
          href: 'https://bk.tencent.com/s-mart/community/',
          target: '_blank',
        },
        {
          name: window.i18n.t('产品官网'),
          href: 'https://bk.tencent.com/index/',
          target: '_blank',
        },
      ];
    }
  },
};
</script>

<style lang="postcss" scoped>
.footer {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 10px;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 52px;
  font-size: 12px;
  p {
    line-height: 16px;
  }
  &-link {
    margin-bottom: 3px;
    &-list {
      padding: 0 4px;
      &:not(:last-child) {
        border-right: 1px solid #63656E;
      }
    }
    &-item {
      display: inline-block;
      color: #3a84ff;
    }
  }
  &-copyright {
    color: #979ba5;
  }
}
</style>
