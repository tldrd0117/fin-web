const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

let config = {
    entry: './src/index.tsx',
    output: {
        filename: 'main.js',
        path: path.resolve(__dirname, 'dist'),
    },
    module:{
        rules:[
            // {
            //     test: /\.tsx?$/,
            //     use: ['ts-loader','babel-loader'],
            //     exclude: /node_modules/,
            // },
            {
                test: /\.tsx?$/,
                exclude: /node_modules/,
                use: [{
                    loader: 'babel-loader',
                }]
            },
            {
                test: /\.html$/,
                use: [{
                    loader: 'html-loader',
                    options: {
                        minimize: true,
                    }
                }]
        
            },{
                test: /\.css$/i,
                use: [
                    "style-loader",
                    "css-loader",
                    "postcss-loader"
                    // {
                    //     loader: "postcss-loader",
                    //     options: {
                    //         postcssOptions: {
                    //             plugins: [
                    //                 [
                    //                 ],
                    //             ]
                    //         },
                    //     }
                    // }
                ]
            }
        ]
            
    },
    plugins:[
        new HtmlWebpackPlugin({
            template: 'public/index.html',
        })
    ],
    resolve:{
        alias:{
            "@": path.resolve(__dirname, "src")
        },
        extensions: ['.tsx', '.ts', '.js'],
    }
};

module.exports = (env, argv) => {
    if(argv.mode == "development"){
        return {
            ...config,
            devtool: "eval",
            watch: true
        }
    } else if(argv.mode == "production"){
        return {
            ...config
        }
    }
}