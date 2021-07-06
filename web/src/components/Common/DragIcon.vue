<template>
    <div class="drag-icon" @mousedown.left="$emit('dragBegin', $event)">
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
        <span class="dot"></span>
    </div>
</template>

<style scoped>
    @import "../../css/variable.css";
    .drag-icon {
        position: absolute;
        top: 50%;
        left: 0;
        display: flex;
        flex-flow: column;
        justify-content: space-between;
        width: 9px;
        height: 36px;
        padding: 9px 3px;
        transform: translateY(-50%);
        z-index: 10;
        cursor: move;
        .dot {
            width: 3px;
            height: 3px;
            border-radius: 50%;
            background: $newBlackColor2;
            transition: background-color .3s;
        }
        &:hover, &.active {
            .dot {
                background: #DCDEE5;
                transition: background-color .3s;
            }
        }
    }
</style>
