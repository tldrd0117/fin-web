
const path = require('path');

module.exports = {
  "stories": [
    "../src/**/*.stories.mdx",
    "../src/**/*.stories.@(js|jsx|ts|tsx)"
  ],
  "addons": [
    "@storybook/addon-links",
    "@storybook/addon-essentials",
    // '@storybook/addon-postcss'
    {
      name: '@storybook/addon-postcss',
      options: {
        postcssLoaderOptions: {
          implementation: require('postcss'),
        },
      },
    },
  ],
  // webpackFinal: (config) => {
  //   return { ...config, module: { ...config.module, rules: 
  //     config.module.rules.concat({
  //       test: /\.css$/i,
  //       use: [
  //           // "style-loader",
  //           // "css-loader",
  //           {
  //           loader:"postcss-loader",
  //           options: {
  //             config: {
  //               path: './',
  //             }
  //           }
  //         }
  //       ],
  //     })
  //   }}
  // },
}