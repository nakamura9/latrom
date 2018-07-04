var path = require("path");
var webpack = require("webpack");
var BundleTracker = require("webpack-bundle-tracker");

module.exports = {
    context: __dirname,
    entry:  {
        quotes: './js/quotes',
        invoicing: './js/invoicing',
        orders: './js/orders',
        payroll: './js/payroll',
        direct_purchase: './js/direct_purchase',
        compound_transaction: './js/compound_transaction',
        stock_receipt: './js/stock_receipt',
        credit_note: './js/credit_note',
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
                    presets: ['react']
                }
            }
        ]
    },

    resolve: {
        extensions: [ '.js', '.jsx']
    }
}