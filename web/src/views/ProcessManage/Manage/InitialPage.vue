<template>
    <div class="initial-page">
        <i class="special-tip-icon bk-icon icon-info"></i>
        <span>{{ $t('请选择服务实例查看') }}</span>
    </div>
</template>

<script>
    export default {

    }
</script>

<style lang="postcss" scoped>
    .initial-page {
        height: 100%;
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #6c6d76;
        font-size: 14px;
        width: 100%;
        i {
            font-size: 18px;
            margin-right: 5px;
        }
    }
</style>
