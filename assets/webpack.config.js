var path = require("path");
var webpack = require("webpack");
var BundleTracker = require("webpack-bundle-tracker");
var terserPlugin = require("terser-webpack-plugin");
var uglifyPlugin = require("uglifyjs-webpack-plugin");

module.exports = {

    context: __dirname,
    entry:  {
        accounting: './js/accounting',
        invoicing: './js/invoicing',
        employees: './js/employees',
        inventory: './js/inventory',
        calendar: './js/calendar',
        services: './js/services',
        manufacturing: './js/manufacturing',
        widgets: './js/widgets'
    },
    output: {
        path: path.resolve('./bundles/'),
        filename: '[name].js',
    },
    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
    ],
    mode: 'development',

    module: {
        rules: [
            {
                test: /\.js$/,
                loader: 'babel-loader',
                exclude: /node_modules/,
                query: {
                    presets: ['stage-2','react']//stage 2 for class level attrs and autobind
                }
            },
            {
                test: /\.css$/,
                loader: 'style-loader'
            },
            {
                test: /\.css$/,
                loader:  'css-loader',
                options: {
                    modules: true,
                    localIdentName: '[name]__[local]__[hash:base64:5]'
                }
            }
        ]
    },

    resolve: {
        extensions: [ '.js', '.jsx']
    },
    /*
    optimization: {
        minimize:true,
        minimizer: [new terserPlugin()]
    }
    */
}