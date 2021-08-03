<template>
  <bk-dialog
    width="768"
    ext-cls="permission-dialog"
    :z-index="2010"
    :draggable="false"
    :mask-close="false"
    :header-position="'left'"
    :title="''"
    :value="isModalShow"
    @cancel="onCloseDialog"
    @after-leave="handleDialogLeave">
    <div
      class="permission-modal"
      v-bkloading="{ isLoading: loading, opacity: 1 }">
      <div class="permission-header">
        <span class="title-icon">
          <img :src="lock" alt="permission-lock" class="lock-img" />
        </span>
        <h3>{{ $t('该操作需要以下权限') }}</h3>
      </div>
      <table class="permission-table table-header">
        <thead>
          <tr>
            <th width="20%">{{ $t('系统') }}</th>
            <th width="30%">{{ $t('需要申请的权限') }}</th>
            <th width="50%">{{ $t('关联的资源实例') }}</th>
          </tr>
        </thead>
      </table>
      <div class="table-content">
        <table class="permission-table">
          <tbody>
            <template v-if="actionsList.length > 0">
              <tr v-for="(action, index) in actionsList" :key="index">
                <td width="20%">{{ action.systemName || '--' }}</td>
                <td width="30%">{{ action.actionName || '--' }}</td>
                <td width="50%">
                  <p
                    class="resource-type-item"
                    v-for="(reItem, reIndex) in getResource(action.related_resource_types)"
                    :key="reIndex">
                    {{reItem}}
                  </p>
                </td>
              </tr>
            </template>
            <tr v-else>
              <td class="no-data" colspan="3">
                {{ $t('无数据') }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div class="permission-footer" slot="footer">
      <div class="button-group">
        <bk-button
          theme="primary"
          :disabled="!url || !actionsList.length"
          :loading="loading"
          @click="goToApply">{{ $t('去申请') }}</bk-button>
        <bk-button theme="default" @click="onCloseDialog">{{ $t('取消') }}</bk-button>
      </div>
    </div>
  </bk-dialog>
</template>
<script>
import { mapState, mapActions } from 'vuex';
import lockSvg from '@/assets/images/lock-radius.svg';

export default {
  name: 'AuthModal',
  props: {},
  data() {
    return {
      url: '',
      isModalShow: false,
      actionsList: [],
      loading: false,
      trigger: '',
      lock: lockSvg,
      id: '', // 业务id | 模板id
      actionName: '',
      actionType: '', // biz | action
    };
  },
  computed: {
    ...mapState(['bizId']),
    resourceType() {
      if (['delete_config_template', 'edit_config_template'].includes(this.actionName)) {
        return 'config_template';
      }
      return 'biz';
    },
  },
  methods: {
    ...mapActions('iam', ['ajaxGetAuthApplyInfo']),
    async loadPermissionUrl() {
      this.loading = true;
      try {
        const params = {
          action_ids: [this.actionName],
          resources: [{
            type: this.resourceType,
            id: (this.actionType === 'biz' || this.resourceType !== 'biz') ? this.id : this.bizId,
          }],
        };
        const res = await this.ajaxGetAuthApplyInfo(params);
        this.formatData(res.data);
      } catch (e) {
        console.warn(e);
      }
      this.loading = false;
    },
    show({ trigger, params, requestData }) {
      this.trigger = trigger;
      this.isModalShow = true;
      if (trigger === 'click') {
        const { id, action, type } = params;
        this.id = id;
        this.actionName = action;
        this.actionType = type;
        this.loadPermissionUrl();
      } else if (trigger === 'request') {
        this.formatData(requestData);
      }
    },
    formatData(res) {
      const { apply_data: applyData, apply_url: applyUrl, permission } = res;
      const data = applyData || permission;
      const { actions = [], system_name: systemName = '' } = data;
      this.actionsList = actions.map(action => ({
        actionName: action.name,
        systemName,
        related_resource_types: action.related_resource_types,
        // actionId: action.id,
        // systemId
      }));
      this.url = applyUrl;
    },
    getResource(resoures) {
      if (resoures.length === 0) {
        return ['--'];
      }

      const data = [];
      resoures.forEach((resource) => {
        if (resource.instances.length > 0) {
          const instances = resource.instances.map(instanceItem => instanceItem.map(item => item.name || item.id).join('，')).join('，');
          const resourceItemData = `${resource.type_name}：${instances}`;
          data.push(resourceItemData);
        }
      });
      return data;
    },
    goToApply() {
      if (this.loading) {
        return;
      }
      if (self === top) {
        window.open(this.url, '__blank');
      } else {
        try {
          window.top.BLUEKING.api.open_app_by_other(
            'bk_iam',
            this.url,
          );
        } catch (_) {
          window.open(this.url, '__blank');
        }
      }
    },
    onCloseDialog() {
      this.isModalShow = false;
    },
    handleDialogLeave() {
      this.actionsList.splice(0, this.actionsList.length);
      this.url = '';
      this.trigger = '';
      this.id = '';
      this.actionName = '';
      this.actionType = '';
    },
  },
};
</script>
<style lang="postcss" scoped>
  .permission-modal {
    .permission-header {
      text-align: center;

      .title-icon {
        display: inline-block;
      }

      .lock-img {
        width: 120px;
      }

      h3 {
        margin: 6px 0 24px;
        color: #63656e;
        font-size: 20px;
        font-weight: normal;
        line-height: 1;
      }
    }

    .permission-table {
      width: 100%;
      color: #63656e;
      border-bottom: 1px solid #e7e8ed;
      border-collapse: collapse;
      table-layout: fixed;

      th,
      td {
        padding: 12px 18px;
        font-size: 12px;
        text-align: left;
        border-bottom: 1px solid #e7e8ed;
        word-break: break-all;
      }

      th {
        color: #313238;
        background: #f5f6fa;
      }
    }

    .table-content {
      max-height: 260px;
      border-bottom: 1px solid #e7e8ed;
      border-top: 0;
      overflow: auto;

      .permission-table {
        border-top: 0;
        border-bottom: 0;

        td:last-child {
          border-right: 0;
        }

        tr:last-child td {
          border-bottom: 0;
        }

        .resource-type-item {
          padding: 0;
          margin: 0;
        }
      }

      .no-data {
        text-align: center;
        color: #999;
      }
    }
  }

  .button-group {
    .bk-button {
      margin-left: 7px;
    }
  }
</style>
