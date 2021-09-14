<template>
  <div class="config-file-container">
    <div class="navigation-content">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConfigFile',
};
</script>

<style scoped>
  .config-file-container {
    height: 100%;
    background-color: #f5f7fa;

    .navigation-content {
      height: 100%;
    }
  }
</style>
