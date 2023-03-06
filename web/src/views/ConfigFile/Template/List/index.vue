<template>
  <div class="config-file-template-list-container" v-test="'configFile'">
    <div class="title">{{ $t('配置文件模板') }}</div>
    <div class="option-group">
      <AuthTag v-test="'addTemp'" action="create_config_template" :authorized="authMap.create_config_template">
        <template slot-scope="{ disabled }">
          <bk-button class="king-button" theme="primary" :disabled="disabled" @click="showCreate = true">
            {{ $t('新建') }}
          </bk-button>
        </template>
      </AuthTag>
      <bk-input
        v-test="'searchTemp'"
        v-model.trim="searchWord"
        :placeholder="$t('请输入文件名或模板名')"
        class="king-input"
        right-icon="icon-search"
        clearable
        @enter="handleSearch"
        @blur="handleSearch"
        @clear="handleSearch"
      ></bk-input>
    </div>
    <bk-table
      v-bkloading="{ isLoading: templateLoading, zIndex: 0 }"
      class="king-table"
      auto-scroll-to-top
      :max-height="$store.state.pageHeight - 190"
      :data="templateList"
      :pagination="pagination"
      @sort-change="handleSortChange"
      @page-change="handlePageChange"
      @page-limit-change="handlePageLimitChange">
      <bk-table-column :label="$t('模板名称')" prop="template_name" sortable="custom">
        <div class="template-name-column" slot-scope="{ row }">
          <AuthTag
            v-bk-overflow-tips
            v-test="'viewTemp'"
            class="button-text"
            action="edit_config_template"
            :id="row.config_template_id"
            :authorized="row.edit_config_template"
            @click="operateVersionList(row)">
            {{ row.template_name }}
          </AuthTag>
          <span
            v-if="!row.has_version"
            v-bk-tooltips="$t('没有可用版本，无法进行配置下发')"
            class="gsekit-icon gsekit-icon-alert"></span>
        </div>
      </bk-table-column>
      <bk-table-column :label="$t('文件名')" prop="file_name" sortable="custom">
        <div v-bk-overflow-tips class="table-ceil-overflow" slot-scope="{ row }">
          <span>{{ row.file_name }}</span>
        </div>
      </bk-table-column>
      <bk-table-column :label="$t('文件所处路径')" prop="abs_path" sortable="custom">
        <div v-bk-overflow-tips class="table-ceil-overflow" slot-scope="{ row }">
          <span>{{ row.abs_path }}</span>
        </div>
      </bk-table-column>
      <bk-table-column :label="$t('关联进程数')">
        <template slot-scope="{ row }">
          <bk-popover v-if="row.is_bound" placement="right">
            <div
              class="button-text" style="min-width: 20px;line-height: 28px;"
              v-test="'numConnect'" @click="operateBind(row)">
              {{ row.relation_count.TEMPLATE + row.relation_count.INSTANCE }}
            </div>
            <div slot="content">
              <div>{{ '模板进程：' + row.relation_count.TEMPLATE }}</div>
              <div>{{ '实例进程：' + row.relation_count.INSTANCE }}</div>
            </div>
          </bk-popover>
          <div v-else v-bk-tooltips="$t('未关联进程，无法进行配置下发，点击关联')"
               class="not-bound-column" v-test="'numConnect'" @click="operateBind(row)">
            <span>{{ $t('未关联') }}</span>
            <span class="gsekit-icon gsekit-icon-alert"></span>
          </div>
        </template>
      </bk-table-column>
      <bk-table-column
        :label="$t('更新人')"
        prop="updated_by"
        :filters="updatePersonFilters"
        :filter-method="commonFilterMethod"
        :filter-multiple="true"
      ></bk-table-column>
      <bk-table-column :label="$t('更新时间')" prop="updated_at" sortable="custom" show-overflow-tooltip>
        <template slot-scope="{ row }">
          {{ formatDate(row.updated_at) }}
        </template>
      </bk-table-column>
      <bk-table-column :label="$t('操作')" :width="operateColWidth">
        <div class="table-operation-container" slot-scope="{ row }">
          <AuthTag class="bk-button-text" action="operate_config" :authorized="authMap.operate_config">
            <div slot-scope="{ disabled }" v-bk-tooltips="{
              content: !row.has_version ? $t('没有可用版本，无法进行配置下发') : $t('未关联进程，无法进行配置下发'),
              disabled: row.has_version && row.is_bound
            }">
              <bk-button
                text theme="primary" :disabled="disabled || !row.has_version || !row.is_bound"
                v-test="'release'"
                @click="operateDistribute(row)">
                {{ $t('配置下发') }}
              </bk-button>
            </div>
          </AuthTag>
          <bk-button v-test="'connectProcess'" theme="primary" text @click="operateBind(row)">
            {{ $t('关联进程') }}
          </bk-button>
          <AuthTag class="bk-button-text" action="operate_config" :authorized="authMap.operate_config">
            <div slot-scope="{ disabled }" v-bk-tooltips="{
              content: $t('未下发配置，无法进行配置检查'),
              disabled: row.has_release
            }">
              <bk-button
                text theme="primary" :disabled="disabled || !row.has_release"
                v-test="'configCheck'"
                @click="operateConfigCheck(row)">
                {{ $t('配置检查') }}
              </bk-button>
            </div>
          </AuthTag>
          <bk-popover
            placement="bottom-start"
            theme="dot-menu light"
            trigger="click"
            :arrow="false"
            offset="15"
            :distance="0">
            <div class="dot-menu-trigger">
              <span class="bk-icon icon-more" v-test.common="'more'"></span>
            </div>
            <ul class="dot-menu-list" slot="content">
              <AuthTag
                tag="li"
                :class="['dot-menu-item cover', { 'disabled': !row.has_version }]"
                v-test.common="'moreItem'"
                action="operate_config"
                :authorized="authMap.operate_config"
                @click="row.has_version && operateGenerate(row)">
                <div
                  style="padding: 0 16px;"
                  slot-scope="{ disabled }"
                  v-bk-tooltips="{
                    content: $t('没有可用版本，无法进行配置生成'),
                    disabled: disabled || row.has_version
                  }">
                  {{ $t('配置生成') }}
                </div>
              </AuthTag>
              <AuthTag
                tag="li"
                class="dot-menu-item"
                v-test.common="'moreItem'"
                action="delete_config_template"
                :id="row.config_template_id"
                :authorized="row.delete_config_template"
                @click="operateDelete(row)">
                {{ $t('删除') }}
              </AuthTag>
            </ul>
          </bk-popover>
        </div>
      </bk-table-column>
      <TableException
        slot="empty"
        :delay="templateLoading"
        :type="tableEmptyType"
        @empty-clear="emptySearchClear" />
    </bk-table>
    <CreateTemplateDialog :show-create.sync="showCreate" @created="handleCreated" />
    <BindProcessDialog
      :template-item="templateItem"
      :show-dialog.sync="showBindProcess"
      @shouldRefreshList="getTemplateList" />
  </div>
</template>

<script>
import { mapGetters, mapState } from 'vuex';
import CreateTemplateDialog from './CreateTemplate/Dialog';
import BindProcessDialog from './BindProcess/Dialog';
import { commonFilterMethod, formatDate } from '@/common/util';

export default {
  name: 'TemplateList',
  components: {
    CreateTemplateDialog,
    BindProcessDialog,
  },
  data() {
    return {
      commonFilterMethod,
      formatDate,
      searchWord: '',
      ordering: '', // 排序字段
      searchedWord: '', // 用来判断相同内容是否搜索过
      templateLoading: true,
      templateList: [],
      updatePersonFilters: [],
      templateItem: {},
      pagination: {
        current: 1,
        count: 0,
        limit: 50,
      },
      showCreate: false,
      showBindProcess: false,
    };
  },
  computed: {
    ...mapState(['authMap']),
    ...mapGetters(['enLang']),
    operateColWidth() {
      return this.enLang ? 340 : 240;
    },
    tableEmptyType() {
      return !!this.searchedWord ? 'search-empty' : 'empty';
    },
  },
  created() {
    this.getTemplateList();
  },
  mounted() {
    // 根据路由自动打开新建弹框
    const { fromPreManage } = this.$route.query;
    if (fromPreManage) {
      this.showCreate = true;
    }
  },
  methods: {
    async getTemplateList() {
      try {
        this.templateLoading = true;
        const res = await this.$store.dispatch('configTemplate/ajaxGetConfigTemplateList', {
          search: this.searchWord,
          ordering: this.ordering,
          page: this.pagination.current,
          pagesize: this.pagination.limit,
        });
        const updatePersonFilters = new Set();
        res.data.list.forEach((item) => {
          item.config_template_id += '';
          updatePersonFilters.add(item.updated_by);
          Object.assign(item, item.permission || {});
        });
        this.updatePersonFilters = [...updatePersonFilters].map(item => ({
          text: item,
          value: item,
        }));
        this.templateList = res.data.list;
        this.pagination.count = res.data.count;
        this.searchedWord = this.searchWord;
      } catch (e) {
        this.templateList.splice(0);
        this.updatePersonFilters.splice(0);
        this.pagination.current = 1;
        this.pagination.count = 0;
        console.warn(e);
      } finally {
        this.templateLoading = false;
      }
    },
    emptySearchClear() {
      this.templateLoading = true;
      this.searchWord = '';
      this.handleSearch();
    },
    handleSearch() {
      if (this.searchWord !== this.searchedWord) {
        this.pagination.current = 1;
        this.getTemplateList();
      }
    },
    handleSortChange({ prop, order }) {
      if (order === 'ascending') {
        this.ordering = prop;
      } else if (order === 'descending') {
        this.ordering = `-${prop}`;
      } else {
        this.ordering = '';
      }
      this.getTemplateList();
    },
    handlePageChange(page) {
      this.pagination.current = page;
      this.getTemplateList();
    },
    handlePageLimitChange(limit) {
      this.pagination.current = 1;
      this.pagination.limit = limit;
      this.getTemplateList();
    },
    // 查看模板版本列表
    operateVersionList(row) {
      this.$emit('selectConfig', row);
      this.$store.commit('routeConfigTemplateVersionList', {
        templateId: row.config_template_id,
      });
    },
    // 配置下发
    operateDistribute(row) {
      this.$emit('selectConfig', row);
      this.$store.commit('routeConfigTemplateDistribute', {
        templateId: row.config_template_id,
      });
    },
    // 配置检查
    operateConfigCheck(row) {
      this.$emit('selectConfig', row);
      this.$store.commit('routeConfigTemplateCheck', {
        templateId: row.config_template_id,
      });
    },
    // 配置生成
    operateGenerate(row) {
      this.$emit('selectConfig', row);
      this.$store.commit('routeConfigTemplateGenerate', {
        templateId: row.config_template_id,
      });
    },
    // 配置预览
    operatePreview(row) {
      this.$emit('selectConfig', row);
      this.$store.commit('routeConfigTemplateVersionDetail', {
        templateId: row.config_template_id,
        versionId: 0,
        isPreview: true,
      });
    },
    // 关联进程
    operateBind(row) {
      this.templateItem = row;
      this.showBindProcess = true;
    },
    // 配置删除
    operateDelete(row) {
      this.$bkInfo({
        title: `${this.$t('确认要删除')}【${row.template_name}】${this.$t('？')}`,
        width: 540,
        confirmLoading: true,
        confirmFn: async () => {
          try {
            await this.$store.dispatch('configTemplate/ajaxDeleteConfigTemplate', {
              templateId: row.config_template_id,
            });
            this.messageSuccess(this.$t('删除成功'));
            this.getTemplateList();
            return true;
          } catch (e) {
            console.warn(e);
            return false;
          }
        },
      });
    },
    // 新建配置模板
    handleCreated(templateId) {
      // todo 有点卡 可以看怎么优化下
      this.$emit('selectConfig', templateId);
    },
  },
};
</script>

<style scoped lang="postcss">
  @import '../../../../css/variable.css';

  .config-file-template-list-container {
    height: 100%;
    padding: 18px 60px 0;

    .title {
      font-size: 16px;
      color: $newBlackColor1;
    }

    .option-group {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin: 20px 0 16px;

      .king-button {
        width: 88px;
      }

      .king-input {
        width: 500px;
      }
    }

    .king-table {
      background: #fff;

      .gsekit-icon-alert {
        flex-shrink: 0;
        color: $newRedColor;
        font-size: 12px;
        line-height: 16px;
        cursor: pointer;
        margin-left: 4px;
      }

      .template-name-column {
        display: flex;

        > .button-text {
          max-width: 100%;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }

      .not-bound-column {
        display: inline-flex;
        cursor: pointer;
        color: $newBlackColor3;

        &:hover {
          color: $newMainColor;
        }
      }
    }
  }
</style>
