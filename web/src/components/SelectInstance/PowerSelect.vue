<template>
  <bk-select
    :value="value"
    :placeholder="$t('全部') + name + '（*）'"
    :popover-min-width="160"
    :list="list"
    multiple
    searchable
    :enable-virtual-scroll="list.length > 50"
    @change="handleChange"
    @selected="handleSelected">
    <template v-for="item in list">
      <bk-option :key="item.id" :id="item.id" :name="item.name"></bk-option>
    </template>
  </bk-select>
  <!--<bk-select :value="value"
    :placeholder="name"
    :clearable="false"
    :popover-min-width="160"
    multiple
    searchable
    @selected="handleChange">
    <bk-option id="*" :name="$t('全部') + name + '（*）'"></bk-option>
    <template v-for="item in list">
      <bk-option :key="item.id" :id="item.id" :name="item.name">
        <div class="bk-option-content-default king-option-container">
          <i class="bk-option-icon bk-icon icon-check-1" v-if="value.includes(item.id)"></i>
          <div v-bk-overflow-tips="{ placement: 'right', content: item.name }" class="bk-option-name">
            {{ item.name }}
          </div>
        </div>
      </bk-option>
    </template>
  </bk-select>-->
</template>

<script>
export default {
  props: {
    list: {
      type: Array,
      required: true,
    },
    value: {
      type: Array,
      required: true,
    },
    name: {
      type: String,
      default: '',
    },
  },
  methods: {
    handleChange(val) {
      this.$emit('change', val);
    },
    handleSelected(value, option) {
      this.$emit('selected', value, option);
    },
  },
};
</script>
