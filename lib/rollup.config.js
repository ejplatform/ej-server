import resolve from 'rollup-plugin-node-resolve';
import babel from 'rollup-plugin-babel';
import flow from 'rollup-plugin-flow';


export default {
    input: 'js/index.js',
    output: {
        file: 'build/js/bundle.js',
        format: 'iife'
    },
    external: ['unpoly'],
    watch: {
        include: 'js/**'
    },
    plugins: [
        flow(),
        resolve(),
        babel({
            exclude: 'node_modules/**'
        })
    ]
};
