var path = require("path");
var webpack = require("webpack");
var BundleTracker = require("webpack-bundle-tracker");


module.exports = {
    context: __dirname,
    entry:  {
        accounting: './js/accounting',
        invoicing: './js/invoicing',
        employees: './js/employees',
        inventory: './js/inventory',
        calendar: './js/calendar',
        services: './js/services',
        widgets: './js/widgets'
    },
    output: {
        path: path.resolve('./bundles/'),
        filename: '[name].js',
    },
    plugins: [
        new BundleTracker({filename: './webpack-stats.json'})
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
            }
        ]
    },

    resolve: {
        extensions: [ '.js', '.jsx']
    }
}