<template>
  <div class="empty-box">
    <div class="empty-top">
      <img :src="imageSrc">
    </div>
    <div class="empty-bottom">
      <div v-if="index !== ''" :class="['empty-status', { 'completed': completed }]">
        <i class="gsekit-icon gsekit-icon-check-line" v-if="completed"></i>
        <span v-else>{{ index }}</span>
      </div>
      <div class="empty-desc">
        <i18n :path="descPath">
          <slot>
            <bk-button v-if="linkBtn" text theme="primary" class="reset-icon-btn" @click="handleClick">
              <span class="flex-content">
                {{ linkBtn }}<i class="gsekit-icon gsekit-icon-jump-fill"></i>
              </span>
            </bk-button>
          </slot>
        </i18n>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EmptyBox',
  props: {
    index: {
      type: [String, Number],
      default: '',
    },
    completed: {
      type: Boolean,
      default: false,
    },
    imageSrc: {
      type: String,
      default: '',
    },
    descPath: {
      type: String,
      default: '',
    },
    linkBtn: {
      type: String,
      default: '',
    },
  },
  methods: {
    handleClick() {
      this.$emit('click');
    },
  },
};
</script>

<style lang="postcss" scoped>
  @import '../../css/variable.css';

  .empty-box {
    width: 330px;

    .empty-top {
      min-height: 320px;
      border-radius: 4px;

      img {
        width: 100%;
      }
    }

    .empty-bottom {
      display: flex;
      justify-content: center;
      align-items: center;
      margin: 13px auto 0;
      width: 320px;
      height: 42px;
      line-height: 17px;
      font-size: 13px;
      border-radius: 2px;
      background: #e6e9f0;
    }

    .empty-status {
      width: 30px;
      line-height: 42px;
      color: $newBlackColor3;
      background: $newGreyColor1;
      text-align: center;

      &.completed {
        background: #18c0a1;

        .gsekit-icon {
          font-size: 14px;
          font-weight: bold;
          color: #fff;
        }
      }
    }

    .empty-desc {
      flex: 1;
      padding: 0 8px;
      line-height: 17px;
      font-size: 13px;
      color: $newBlackColor2;
      text-align: center;

      .bk-button-text {
        font-size: 13px;
      }
    }
  }
</style>
