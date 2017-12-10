import React from 'react';
import Dropzone from 'react-dropzone'
import request from 'superagent';


export default class Uploader extends React.Component {
  constructor() {
    super()
    this.state = { disabled: false, accepted: [], rejected: [] }
  }

  onDrop(accepted ,rejected) {
  	var callback = function(err, res) {
     	if (err || !res.ok) {
       		alert('Oh no! error');
     	} else {
     	  	var accepted = this.state.accepted;
     	  	var fileStatusMap = JSON.parse(res.text);
     	  	for (var fileName in fileStatusMap) {
     	  		for (var c=0; c<accepted.length; c++) {
     	  			if (accepted[c].name === fileName) {
     	  				accepted[c].status = fileStatusMap[fileName];
     	  			}
     	  		}
     	  	}
     	  	this.setState({
     	  		accepted: accepted
     	  	})
     	}
  	}
    var req = request.post('/upload/');
    accepted.forEach(file => {
        req.attach(file.name, file);
    });
    req.end(callback.bind(this));

    var currAccepted = this.state.accepted;
    for (var c=0; c<accepted.length; c++) {
    	accepted[c].status = "Uploading..."
    	currAccepted.push(accepted[c]);
    }

    var currRejected = this.state.rejected;
    for (var c=0; c<rejected.length; c++) {
    	currRejected.push(rejected[c])
    }

    this.setState({
      accepted: currAccepted,
      rejected: currRejected
    });
  }

  generateFileView(file) {
  	var isError = false;
  	var colorClass = "hyellow";
  	if (file.status === "success") {
  		colorClass = "hgreen";
  	} else if (file.status.indexOf("error") !== -1) {
  		colorClass = "hred";
  		isError = true;
  	}

  	var status;
  	if (isError) {
  		status = (
            <p>
            	Status: {file.status} [<a href="#a">delete</a>]
            </p>
  		)
  	} else {
  		status = (
            <p>
            	Status: {file.status}
            </p>
  		)
  	}

  	return (
  		<div className={"hpanel " + colorClass} style={{marginBottom: "10px"}}>
            <div className="panel-body" style={{padding:"0px", paddingLeft:"10px", paddingRight: "10px"}}>
                <div className="row">
                    <div className="col-sm-12">
                        <h4 style={{fontWeight: "300", fontFamily: "Open Sans"}}>Filename: {file.name}</h4>
                        {status}
                    </div>
                </div>
            </div>
        </div>
  	)
  }

  render() {
  	var acceptedFiles;
    var statusTracker;

  	if (this.state.accepted.length > 0) {
  		acceptedFiles = (
  			<div>
      			<h4 style={{fontWeight: "300", marginTop: "0px"}}>Uploaded Files</h4>
				    {this.state.accepted.map(f => this.generateFileView(f))}
  			</div>
  		)
      statusTracker = (
          <div className="col-lg-9">  
            {acceptedFiles}           
          </div>
      ) 

  	}  else {
      statusTracker = (
          <div className="col-lg-9">  
            <h4 style={{fontWeight: "300", marginTop: "0px"}}>Status Tracker</h4>
            <p>No files have been queued up for upload yet.</p>          
          </div>
      )
    }

    return (
      	<div className="row">
      		<div className="col-lg-3">
      			<h4 style={{fontWeight: "300", marginTop: "0px"}}>File Dropper</h4>
	        	<div className="dropzone">
	          		<Dropzone accept="text/csv" className="dropzone-component" activeClassName="dropzone-component-active" onDrop={this.onDrop.bind(this)} disabled={this.state.disabled}>
	            		<p>Drag and drop files into this box here to upload!</p>
	          		</Dropzone>
	        	</div>
      		</div>
          {statusTracker}

      	</div>
    );
  }
}
