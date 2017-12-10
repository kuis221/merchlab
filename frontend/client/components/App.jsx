import React from 'react';
import Dropzone from 'react-dropzone'
import request from 'superagent';
import Uploader from './Uploader.jsx'

export default class App extends React.Component {
  constructor() {
    super()
  }

  render() {
    return (
        <div>
            <p>Upload Merch by Amazon Sales Reports into our database to track your monthly figures regularly.
            Click <a href="#a">here</a> to learn more about how to get this report from Amazon.
            </p>

            <hr />
            <Uploader />
        </div>
    );
  }
}
