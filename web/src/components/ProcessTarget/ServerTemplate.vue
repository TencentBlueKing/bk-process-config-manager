<template>
  <div class="server-template">
    <ul>
      <li
        v-for="item in templateList"
        :key="item.id"
        @click="handleClick(item)">
        <div :class="['template-list-item', { 'active': item.active }]" v-show="item.visible">
          <i class="item-icon">{{ $t('模') }}</i>
          <span v-bk-overflow-tips>{{item.name}}</span>
          <i
            v-if="item.showSync"
            class="gsekit-icon gsekit-icon-swither-small sync-icon"
            v-bk-tooltips.top="$t('未同步')"
            @click.stop="goSyncTemplate(item)">
          </i>
        </div>
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'ServerTemplate',
  props: {
    list: {
      type: Array,
      default: () => [],
    },
    searchWord: {
      type: String,
      default: '',
    },
  },
  computed: {
    templateList() {
      return this.searchWord
        ? this.list.filter(item => item.name.includes(this.searchWord)) : this.list;
    },
  },
  methods: {
    handleClick(val) {
      this.setAtive(val);
      this.$emit('click', val);
    },
    cancelActive() {
      this.templateList.forEach((item) => {
        item.active = false;
      });
    },
    setAtive(child) {
      this.templateList.forEach((item) => {
        item.active = item.id === child.id;
      });
    },
    goSyncTemplate(item) {
      console.log(item);
      const cmdbUrl = window.PROJECT_CONFIG.CMDB_URL;
      const { bizId } = this.$store.state;
      window.open(`${cmdbUrl}/#/business/${bizId}/service/operational/template/${item.id}?tab=instance`);
    },
  },
};
</script>

<style lang="postcss" scoped>
  .server-template {
    width: 100%;

    .template-list-item {
      position: relative;
      height: 36px;
      width: 100%;
      color: #63656e;
      font-size: 14px;
      display: flex;
      align-items: center;
      cursor: pointer;
      padding: 0 20px;

      span {
        word-break: keep-all;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .item-icon {
        height: 20px;
        width: 20px;
        border-radius: 50%;
        text-align: center;
        line-height: 20px;
        font-style: normal;
        font-size: 12px;
        background: #97aed6;
        color: #fff;
        flex-shrink: 0;
        margin-right: 7px;
      }

      .sync-icon {
        position: absolute;
        top: 7px;
        right: 20px;
        font-size: 22px;
        color: #c4c6cc;

        &:hover {
          color: #3a84ff;
        }
      }

      &:hover {
        background-color: #e1ecff;
        transition: background-color .2s;
      }
    }

    .active {
      color: #3a84ff;
      background: #e1ecff;

      .item-icon {
        background: #3a84ff;
      }
    }

    .not-server-template {
      height: 100%;
      width: 100%;
      color: #63656e;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  }
</style>
