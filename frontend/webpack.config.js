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
        designer_assignments: './client/designer_assignments.js',
        assignment: './client/assignment.js',
        designers: './client/designers.js',
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
