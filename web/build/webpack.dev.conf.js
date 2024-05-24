/**
 * @file webpack dev conf
 * @author blueking
 */

import path from 'path'

import webpack from 'webpack'
import merge from 'webpack-merge'
import HtmlWebpackPlugin from 'html-webpack-plugin'
import FriendlyErrorsPlugin from 'friendly-errors-webpack-plugin'

import config from './config'
import baseConf from './webpack.base.conf'

const webpackConfig = merge(baseConf, {
    mode: 'development',
    entry: {
        main: './src/main.js'
    },

    module: {
        rules: [
            {
                test: /\.(css|postcss)$/,
                use: [
                    'vue-style-loader',
                    {
                        loader: 'css-loader',
                        options: {
                            importLoaders: 1
                        }
                    },
                    {
                        loader: 'postcss-loader',
                        options: {
                            config: {
                                path: path.resolve(__dirname, '..', 'postcss.config.js')
                            }
                        }
                    }
                ]
            }
        ]
    },

    plugins: [
        new webpack.DefinePlugin(config.dev.env),

        new webpack.HotModuleReplacementPlugin(),

        new webpack.NoEmitOnErrorsPlugin(),

        new HtmlWebpackPlugin({
            filename: 'index.html',
            template: 'index-dev.html',
            favicon: path.resolve(__dirname, '../src/assets/images/favicon.png'),
            chunksSortMode: 'none'
        }),
        new HtmlWebpackPlugin({
            filename: 'login_success.html',
            template: 'login_success.html',
        }),

        new FriendlyErrorsPlugin()
    ]
})

Object.keys(webpackConfig.entry).forEach(name => {
    webpackConfig.entry[name] = ['./build/dev-client'].concat(webpackConfig.entry[name])
})

export default webpackConfig
