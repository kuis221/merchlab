/*
    ./webpack.config.js
*/
const path = require('path');
module.exports = {
    entry: {
        index: './client/index.js',
        dashboard: './client/dashboard.js',
        favorites: './client/favorites.js',
        assignments: './client/assignments.js',
        assignment: './client/assignment.js',
    },
    output: {
        path: path.resolve(__dirname, '../static/bundle'),
        filename: '[name].js'
    },
    module: {
        loaders: [
            { test: /\.js$/, loader: 'babel-loader', exclude: /node_modules/ },
            { test: /\.jsx$/, loader: 'babel-loader', exclude: /node_modules/ }
        ]
    },
}
