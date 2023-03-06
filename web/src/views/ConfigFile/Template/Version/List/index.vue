<template>
  <div class="version-list-container" v-bkloading="{ isLoading: versionLoading }">
    <div class="template-title" style="padding-bottom: 9px;">
      <span class="gsekit-icon gsekit-icon-down-line" @click="$store.commit('routeConfigTemplateList')"></span>
      <span class="text">{{ displayTitle }}</span>
    </div>
    <!-- 该配置模板的一些基本字段信息 -->
    <TemplateFieldList :selected-config.sync="selectedConfig" @change="updateSelectedConfig" />
    <div class="version-list">
      <div class="version-top-container">
        <bk-button style="min-width: 104px;" v-test="'addVersion'" theme="primary" @click="handleCreate">
          {{ $t('新建版本') }}
        </bk-button>
        <bk-input
          v-test="'searchDesc'"
          v-model="searchKeyword"
          style="width: 480px;"
          right-icon="icon-search"
          :clearable="true"
          :placeholder="$t('搜索版本描述')"
          @change="handleSearch"
        ></bk-input>
      </div>
      <bk-table
        v-bkloading="{ isLoading: tableLoading, zIndex: 0 }"
        class="king-table"
        :data="searchedVersionList"
        :max-height="$store.state.pageHeight - 280"
        @row-click="handleRowClick">
        <bk-table-column :label="$t('版本ID')" min-width="150">
          <template slot-scope="{ row }">
            <bk-button v-test="'viewVersion'" theme="primary" text>{{ row.config_version_id }}</bk-button>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('版本描述')" min-width="300">
          <div class="version-description" slot-scope="{ row }">
            <span v-bk-overflow-tips
                  :class="{ 'lighten-text': !row.is_draft && !row.is_active, 'text-overflow-row': true }">
              {{ row.description }}
            </span>
            <TagDraft v-if="row.is_draft" />
            <TagAvailable v-else-if="row.is_active" />
          </div>
        </bk-table-column>
        <bk-table-column
          :label="$t('更新人')"
          min-width="150"
          :filters="updatePersonFilters"
          :filter-method="commonFilterMethod"
          :filter-multiple="true">
          <template slot-scope="{ row }">
            <div :class="{ 'lighten-text': !row.is_draft && !row.is_active }">{{ row.updated_by }}</div>
          </template>
        </bk-table-column>
        <bk-table-column
          :label="$t('更新时间')"
          min-width="220"
          sortable
          :sort-method="sortByDate('updated_at')"
          v-bk-overflow-tips>
          <template slot-scope="{ row }">
            <div :class="{ 'lighten-text': !row.is_draft && !row.is_active }">{{ formatDate(row.updated_at) }}</div>
          </template>
        </bk-table-column>
        <bk-table-column :label="$t('操作')" min-width="200">
          <template slot-scope="{ row }">
            <div class="button-container">
              <span class="button-text">{{ row.is_draft ? $t('编辑') : $t('查看') }}</span>
              <span v-if="!row.is_draft" v-test="'copy'" class="button-text" @click.stop="handleCopyAndCreate(row)">
                {{ $t('复制并新建') }}
              </span>
              <template v-if="row.is_active">
                <AuthTag
                  v-if="selectedConfig.is_bound"
                  v-test="'configRelease'"
                  :class="['button-text', { 'is-disabled': !authMap.operate_config }]"
                  action="operate_config"
                  :authorized="authMap.operate_config"
                  @click="handleDistributeConfig">
                  {{ $t('配置下发') }}
                </AuthTag>
                <span v-else v-bk-tooltips="$t('未关联进程，无法进行配置下发')" @click.stop class="button-text is-disabled">
                  {{ $t('配置下发') }}
                </span>
              </template>
            </div>
          </template>
        </bk-table-column>
        <bk-exception slot="empty" class="empty-box-container" type="empty" scene="part">
          <template v-if="versionList.length && (searchKeyword || tableLoading)">
            <span>{{ $t('未搜索到匹配版本') }}</span>
          </template>
          <template v-else>
            <span>{{ $t('当前配置模板下暂无版本') }}</span>
            <div class="button-text" @click="handleCreate">{{ $t('新建版本') }}</div>
          </template>
        </bk-exception>
      </bk-table>
    </div>

    <!-- 创建新版本 -->
    <CreateDraft
      :show-dialog.sync="showCreateDialog"
      :version-list="versionList"
      @newVersion="handleNewCreate"
      @created="handleSuccessCreated" />
    <!-- 复制并新建 -->
    <CoverDialog
      :show.sync="showCoverDialog"
      :version-list="versionList"
      :cover-version="coverVersion"
      @close="closeCoverDialog"
      @coverSuccess="handleCoverSuccess" />
  </div>
</template>

<script>
import { mapState } from 'vuex';
import TemplateFieldList from './TemplateFieldList';
import CreateDraft from './CreateDraft';
import TagAvailable from '../TagAvailable';
import CoverDialog from '@/views/ConfigFile/Template/Version/Detail/CoverDialog';
import TagDraft from '../TagDraft';
import { sortByDate, commonFilterMethod, formatDate } from '@/common/util';

export default {
  name: 'VersionList',
  components: {
    TemplateFieldList,
    CreateDraft,
    CoverDialog,
    TagAvailable,
    TagDraft,
  },
  props: {
    selectedConfig: {
      type: Object,
      required: true,
    },
    versionList: {
      type: Array,
      required: true,
    },
    displayTitle: {
      type: String,
      default: '',
    },
    versionLoading: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    return {
      sortByDate,
      commonFilterMethod,
      formatDate,
      showCreateDialog: false,
      showCoverDialog: false, // 复制并新建、覆盖草稿
      coverVersion: null, // 要覆盖草稿的可用版本
      searchKeyword: '',
      searchTimer: null,
      searchConfirmKeyword: '',
      tableLoading: false,
      updatePersonFilters: [],
    };
  },
  computed: {
    ...mapState(['authMap']),
    searchedVersionList() {
      return this.versionList.filter(item => item.description.includes(this.searchConfirmKeyword));
    },
  },
  watch: {
    versionList: {
      handler(val) {
        const updatePersonFilters = new Set();
        val.forEach((item) => {
          updatePersonFilters.add(item.updated_by);
        });
        this.updatePersonFilters = [...updatePersonFilters].map(item => ({
          text: item,
          value: item,
        }));
      },
      immediate: true,
    },
  },
  methods: {
    handleSearch(val) { // 搜索版本描述
      this.tableLoading = true;
      this.searchTimer && clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => {
        this.tableLoading = false;
        this.searchConfirmKeyword = val;
      }, 300);
    },
    handleRowClick(row) { // 查看版本
      this.$emit('clickVersionRow', row);
    },

    async handleCopyAndCreate(row) { // 复制并新建
      if (this.versionList.some(item => item.is_draft)) { // 是否覆盖草稿
        this.coverVersion = row;
        this.showCoverDialog = true;
      } else { // 直接以此克隆并新增草稿
        try {
          this.$emit('update:versionLoading', true);
          const res = await this.$store.dispatch('configVersion/ajaxCreateConfigVersion', {
            versionId: row.config_version_id,
            data: {
              description: row.description,
            },
          });
          this.messageSuccess(this.$t('成功创建新版本'));
          this.$emit('createNewVersion', res.data);
          this.$store.commit('routeConfigTemplateVersionDetail', {
            templateId: this.$route.params.templateId,
            versionId: res.data.config_version_id,
          });
        } catch (e) {
          console.warn(e);
        } finally {
          this.$emit('update:versionLoading', false);
        }
      }
    },
    handleCoverSuccess(versionId, version) { // 覆盖草稿，实际修改
      const draftVersion = this.versionList.find(item => item.is_draft);
      Object.assign(draftVersion, {
        description: version.description,
        content: version.content,
        file_format: version.codeLanguage,
        updated_at: version.updated_at,
        updated_by: version.updated_by,
      });
      this.showCoverDialog = false;
      this.coverVersion = null;
      this.$store.commit('routeConfigTemplateVersionDetail', {
        templateId: this.$route.params.templateId,
        versionId,
      });
    },
    closeCoverDialog() {
      this.showCoverDialog = false;
      this.coverVersion = null;
    },

    handleDistributeConfig() { // 配置下发
      this.$store.commit('routeConfigTemplateDistribute', {
        templateId: this.$route.params.templateId,
      });
    },
    handleCreate() { // 新建版本
      const firstVersion = this.versionList[0];
      if (!firstVersion) {
        // 新建草稿
        this.handleNewCreate();
      } else if (firstVersion.is_draft) {
        // 当前已有草稿，是否继续编辑
        this.$bkInfo({
          title: this.$t('当前已有草稿，是否继续编辑？'),
          confirmFn: () => {
            this.$store.commit('routeConfigTemplateVersionDetail', {
              templateId: this.$route.params.templateId,
              versionId: firstVersion.config_version_id,
            });
          },
        });
      } else {
        // 载入版本克隆草稿
        this.showCreateDialog = true;
      }
    },
    async handleNewCreate() { // 新建一个全新的版本（不载入其他版本）
      this.$store.commit('routeConfigTemplateVersionDetail', {
        templateId: this.$route.params.templateId,
        versionId: '0',
      });
    },
    handleSuccessCreated(versionId) {
      this.$emit('updateVersionList', versionId);
    },
    updateSelectedConfig({ key, value }) {
      this.$emit('change', { key, value });
    },
  },
};
</script>

<style scoped lang="postcss">
  @import '../../../../../css/variable.css';

  .version-list-container {
    height: 100%;

    .version-list {
      height: calc(100% - 131px);
      overflow: auto;
      padding: 20px 60px 0;
      background: #fff;

      .version-top-container {
        display: flex;
        justify-content: space-between;
      }

      .king-table {
        margin-top: 16px;

        /deep/ .is-prepend {
          :hover {
            background: transparent;
          }
        }

        /deep/ .bk-table-row {
          cursor: pointer;
        }

        .version-description {
          display: flex;
          align-items: center;
          font-size: 12px;
          line-height: 16px;
        }

        .button-container {
          display: flex;
          align-items: center;
          line-height: 20px;

          .button-text:not(:last-child) {
            margin-right: 10px;
          }
        }

        .lighten-text {
          color: $newBlackColor3;
        }

        >>> .bk-table-empty-text {
          padding-top: 0;

          .empty-box-container {
            font-size: 14px;
            color: $newBlackColor2;

            .bk-exception-text {
              margin-top: -14px;

              .button-text {
                margin-top: 10px;
              }
            }

            .bk-exception-img {
              height: 150px;
            }
          }
        }
      }
    }
  }
</style>
