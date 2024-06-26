const HtmlWebpackPlugin = require('html-webpack-plugin')
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const webpack = require('webpack')
const path = require('path')

module.exports = {
  entry: {
    app: './src/index.js',
  },
  output: {
    publicPath: "/", /// ahhh ;)
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].bundle.js',
    clean: true
  },
  externals: {
    url: 'url',
  },
  devtool: 'source-map',
  optimization: {
    runtimeChunk: {
      name: 'runtime',
    },
    splitChunks: {
      chunks: 'async',
      minSize: 20000,
      minRemainingSize: 0,
      minChunks: 1,
      maxAsyncRequests: 30,
      maxInitialRequests: 30,
      enforceSizeThreshold: 50000,
      cacheGroups: {
        defaultVendors: {
          test: /[\\/]node_modules[\\/]/,
          priority: -10,
          reuseExistingChunk: true,
        },
        default: {
          minChunks: 2,
          priority: -20,
          reuseExistingChunk: true,
        },
      },
    },
  },
  devServer: {
    hot: true,
    open: true,
    historyApiFallback: true,
    proxy: [
      {
        context: ['/api'],
        target: 'http://localhost:3000',
        router: () => 'http://localhost:8080',
        logLevel: 'debug'
      },
      {
        context: ['/socket.io'],
        target: 'http://localhost:3000',
        router: () => 'http://localhost:8080',
        logLevel: 'debug'
      }
    ]
  },
  module: {
    rules: [
      {
        test: /\.riot$/,
        exclude: /node_modules/,
        use: [{
          loader: '@riotjs/webpack-loader',
          options: {
            hot: true,
            sourceMap: true,
            defaultExport: true,
          }
        }],
      },
      {
        test: /\.css$/i,
        use: [MiniCssExtractPlugin.loader, "css-loader"],
      },
      {
        test: /\.(png|svg|jpg|jpeg|gif|ico)$/i,
        type: 'asset/resource',
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/i,
        type: 'asset/resource',
      },
      {
        assert: { type: "css" },
        loader: "css-loader",
        options: {
          exportType: "css-style-sheet",
        },
      },
    ],
  },
  
  plugins: [
    new MiniCssExtractPlugin({
      linkType: "text/css",
      filename: "[name].css",
      chunkFilename: "[id].css",
      insert: "#some-element",
      ignoreOrder: true,
    }),
    new HtmlWebpackPlugin({
      template: 'src/index.html',
      favicon: 'src/favicon.ico'
    }),
    new webpack.HotModuleReplacementPlugin(),
  ]
}
