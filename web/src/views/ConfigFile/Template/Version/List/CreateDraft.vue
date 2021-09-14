<template>
  <bk-dialog :value="showDialog"
             :title="$t('新建版本')"
             :loading="isLoading"
             :mask-close="false"
             width="480"
             ext-cls="create-version-dialog"
             header-position="left"
             @confirm="handleConfirm"
             @value-change="handleValueChange">
    <div style="margin: -10px 0 8px;">{{ $t('选择载入版本') }}</div>
    <bk-select v-model="selectedVersionId" ref="select" style="width: 430px;" :clearable="false">
      <div slot="trigger" class="bk-select-name">
        {{ selectedVersionName }}
        <TagAvailable v-if="isActiveVersion" />
      </div>
      <bk-option id="__EMPTY" :name="$t('不载入任何版本')"></bk-option>
      <template v-for="option in versionList">
        <bk-option :key="option.config_version_id" :id="option.config_version_id" :name="option.description">
          <div class="option-name">
            <span class="id">#{{ option.config_version_id }}</span>
            <span class="description">{{ option.description }}</span>
            <TagAvailable v-if="option.is_active" />
          </div>
        </bk-option>
      </template>
    </bk-select>
  </bk-dialog>
</template>

<script>
import TagAvailable from '../TagAvailable';

export default {
  components: {
    TagAvailable,
  },
  props: {
    showDialog: {
      type: Boolean,
      default: false,
    },
    versionList: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      selectedVersionId: '',
      selectedVersionName: '',
      isActiveVersion: false, // 可用的版本
      isLoading: false,
    };
  },
  watch: {
    showDialog(val) {
      if (val) { // 能打开这个页面，versionList 长度必不为 0
        this.selectedVersionId = this.versionList[0].config_version_id;
      }
    },
    selectedVersionId(val) {
      if (val === '__EMPTY') {
        this.selectedVersionName = this.$t('不载入任何版本');
        this.isActiveVersion = false;
      } else {
        const target = this.versionList.find(item => item.config_version_id === val);
        this.selectedVersionName = `#${target.config_version_id} ${target.description}`;
        this.isActiveVersion = target.is_active;
      }
    },
  },
  methods: {
    handleValueChange(val) {
      this.$emit('update:showDialog', val);
    },
    async handleConfirm() {
      if (this.selectedVersionId === '__EMPTY') {
        this.$emit('update:showDialog', false);
        this.$emit('newVersion'); // 不载入任何版本，新建草稿
        return;
      }
      try {
        this.isLoading = true;
        const res = await this.$store.dispatch('configVersion/ajaxCreateConfigVersion', {
          versionId: this.selectedVersionId,
          data: {
            description: this.versionList.find(item => item.config_version_id === this.selectedVersionId).description,
          },
        });
        this.$emit('update:showDialog', false);
        this.$emit('created', res.data.config_version_id.toString());
      } catch (e) {
        console.warn(e);
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>
