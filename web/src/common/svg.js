const div = document.createElement('div');
/*
 <svg class="svg-icon" aria-hidden="true">
 <use xlink:href="#gsekit-icon-loading"></use>
 </svg>
 */
div.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" style="position:absolute;width:0;height:0;visibility:hidden">
        <symbol id="gsekit-icon-loading" viewBox="0 0 1024 1024">
            <path fill="#3a84ff" d="M512 67.623c37.675 0 67.623 32.845 67.623 73.419v47.335c0 40.574-29.948 73.42-67.623 73.42-37.675 0-67.623-32.846-67.623-73.42v-47.335c0-40.574 29.948-73.42 67.623-73.42z">
                <animate fill="remove" accumulate="none" additive="replace" attributeName="opacity" begin="-0.875s" calcMode="linear" dur="1s" keyTimes="0;1" repeatCount="indefinite" restart="always" values="1;0"></animate>
            </path>
            <path fill="#3a84ff" d="M825.931 197.486c26.64 26.641 24.591 71.042-4.099 99.732l-33.471 33.471c-28.69 28.69-73.09 30.74-99.731 4.099-26.641-26.64-24.592-71.042 4.098-99.731l33.472-33.472c28.69-28.69 73.773-30.056 99.731-4.099z">
                <animate fill="remove" accumulate="none" additive="replace" attributeName="opacity" begin="-0.75s" calcMode="linear" dur="1s" keyTimes="0;1" repeatCount="indefinite" restart="always" values="1;0"></animate>
            </path>
            <path fill="#3a84ff" d="M956.377 512c0 37.675-32.845 67.623-73.419 67.623h-47.335c-40.574 0-73.42-29.948-73.42-67.623 0-37.675 32.846-67.623 73.42-67.623h47.335c40.574 0 73.42 29.948 73.42 67.623z">
                <animate fill="remove" accumulate="none" additive="replace" attributeName="opacity" begin="-0.625s" calcMode="linear" dur="1s" keyTimes="0;1" repeatCount="indefinite" restart="always" values="1;0"></animate>
            </path>
            <path fill="#3a84ff" d="M825.931 825.931c-26.64 26.64-71.042 24.591-99.731-4.099l-33.472-33.471c-28.69-28.69-30.74-73.09-4.098-99.731 26.64-26.641 71.041-24.592 99.73 4.098l34.156 34.155c28.69 28.69 30.056 72.407 3.415 99.048z">
                <animate fill="remove" accumulate="none" additive="replace" attributeName="opacity" begin="-0.5s" calcMode="linear" dur="1s" keyTimes="0;1" repeatCount="indefinite" restart="always" values="1;0"></animate>
            </path>
            <path fill="#3a84ff" d="M512 956.377c-37.675 0-67.623-32.845-67.623-73.419v-47.335c0-40.574 29.948-73.42 67.623-73.42 37.675 0 67.623 32.846 67.623 73.42v47.335c0 40.574-29.948 73.42-67.623 73.42z">
                <animate fill="remove" accumulate="none" additive="replace" attributeName="opacity" begin="-0.375s" calcMode="linear" dur="1s" keyTimes="0;1" repeatCount="indefinite" restart="always" values="1;0"></animate>
            </path>
            <path fill="#3a84ff" d="M197.486 825.931c-26.64-26.64-24.59-71.042 4.099-99.731l33.472-33.472c28.69-28.69 73.09-30.74 99.73-4.098 26.642 26.64 24.592 71.041-4.098 99.73l-33.471 33.472c-28.69 28.69-73.09 30.74-99.732 4.099z">
                <animate fill="remove" accumulate="none" additive="replace" attributeName="opacity" begin="-0.25s" calcMode="linear" dur="1s" keyTimes="0;1" repeatCount="indefinite" restart="always" values="1;0"></animate>
            </path>
            <path fill="#3a84ff" d="M67.623 512c0-37.675 32.845-67.623 73.419-67.623h47.335c40.574 0 73.42 29.948 73.42 67.623 0 37.675-32.846 67.623-73.42 67.623h-47.335c-40.574 0-73.42-29.948-73.42-67.623z">
                <animate fill="remove" accumulate="none" additive="replace" attributeName="opacity" begin="-0.125s" calcMode="linear" dur="1s" keyTimes="0;1" repeatCount="indefinite" restart="always" values="1;0"></animate>
            </path>
            <path fill="#3a84ff" d="M197.486 197.486c26.641-26.64 71.042-24.59 99.732 4.099l33.471 33.472c28.69 28.69 30.74 73.09 4.099 99.73-26.64 26.642-71.042 24.592-99.731-4.098l-33.472-33.471c-28.69-28.69-30.74-73.09-4.099-99.732z">
                <animate fill="remove" accumulate="none" additive="replace" attributeName="opacity" begin="0s" calcMode="linear" dur="1s" keyTimes="0;1" repeatCount="indefinite" restart="always" values="1;0"></animate>
            </path>
        </symbol>
    </svg>
`;
document.body.insertBefore(div, document.getElementById('app'));
