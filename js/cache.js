/**
 * js实现cache结果的功能
 */

function cached(fn) {
    const cache = Object.create(null);
    return function (str) {
        return cache[str] || (cache[str] = fn(str));
    };
}

const capitalize = cached((str) => {
    return str.charAt(0).toUpperCase() + str.slice(1);
});