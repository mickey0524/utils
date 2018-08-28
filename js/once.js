/**
 * js控制只执行一次函数
 */

function once(fn) {
    return function () {
        if (!fn.called) {
            fn.called = true;
            fn.apply(this, arguments);
        }
    }
}