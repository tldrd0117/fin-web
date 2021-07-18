
const purgecss = require('@fullhuman/postcss-purgecss')
module.exports ={
    plugins: [
        require('postcss-nested'),
        require('tailwindcss'),
        require('autoprefixer'),
        // purgecss({
        //     content: ['./**/*.html','./**/*.css','./**/*.js','./**/*.jsx','./**/*.tsx']
        // })
    ]
};