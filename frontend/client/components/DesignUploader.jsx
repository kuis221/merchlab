import React from 'react';
import Dropzone from 'react-dropzone'
import request from 'superagent';


export default class DesignUploader extends React.Component {
	constructor() {
		super()
		this.state = { disabled: false, accepted: [], rejected: [] }
	}

	onDrop(accepted ,rejected) {
		var callback = function(err, res) {
			if (err || !res.ok) {
					//alert('Oh no! error');
			} else {
				var accepted = this.state.accepted;
				var fileStatusMap = JSON.parse(res.text);
				console.log(fileStatusMap)
				for (var fileName in fileStatusMap) {
					for (var c=0; c<accepted.length; c++) {
						if (accepted[c].name === fileName) {
							accepted[c].meta = fileStatusMap[fileName];
							console.log("this is the file", accepted[c].name, accepted[c].meta)
							var url = "https://s3.amazonaws.com/" + accepted[c].meta.s3_bucket_name + "/" + accepted[c].meta.s3_filename;
							var upload_uuid = accepted[c].meta.upload_uuid;
							console.log(url);
							var work = {
								s3_url: url,
								approved: false
							}
							this.props.update(upload_uuid, work);
						}
					}
				}
				this.setState({
					accepted: accepted
				})
			}
		}
		var req = request.post('/assignment/' + this.props.assignment_id + '/upload/');
		accepted.forEach(file => {
				req.attach(file.name, file);
		});
		req.end(callback.bind(this));

		var currAccepted = this.state.accepted;
		for (var c=0; c<accepted.length; c++) {
			accepted[c].job_status = "Uploading..."
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

	startOver() {
		this.setState({
			accepted: [],
			rejected: []
		})
	}

	jsUcfirst(string) {
    	return string.charAt(0).toUpperCase() + string.slice(1);
	}

	generateFileView(file) {


		var status;
		if (file.meta && file.meta.job_status && file.meta.job_status.toLocaleLowerCase().indexOf("error") !== -1) {
			status = (
				<div className="col-sm-11" style={{textAlign: "left"}}>
					<i className="fa fa-times-circle-o fa-2x fa-fw pull-right"></i>
					<h5 style={{fontWeight: "600", fontFamily: "Open Sans", marginTop: "0px"}}>Filename: {file.name}</h5>
					<p style={{fontWeight: "300", fontFamily: "Open Sans"}}>
						Status: {this.jsUcfirst(file.meta.job_status) + ". " + file.meta.error_message}
					</p>
					<div className="progress">
						<div className="determinate" style={{width: "100%", backgroundColor: "#e74c3c"}}></div>
					</div>
				</div>
			)
		} else if (file.meta && file.meta.job_status && file.meta.job_status.toLocaleLowerCase().indexOf("uploaded") !== -1) { 
			return (<div style={{display:'none'}}></div>)
		} else {
			status = (
				<div className="col-sm-11" style={{textAlign: "left"}}>
					<i className="fa fa-spinner fa-spin fa-2x fa-fw pull-right"></i>
					<h5 style={{fontWeight: "600", fontFamily: "Open Sans", marginTop: "0px"}}>Filename: {file.name}</h5>
					<p style={{fontWeight: "300", fontFamily: "Open Sans", marginBottom: "0px"}}>
						Status: {file.meta ? file.meta.job_status : "Uploading..."}
					</p>
					<div className="progress">
						<div className="indeterminate"></div>
					</div>
				</div>
			)
		}

		return (
			<div className="hpanel" style={{marginBottom: "20px"}}>
				<div className="panel-body" style={{padding:"0px", paddingLeft:"10px", paddingRight: "10px", border:"0px"}}>
					<div className="row">
						<div className="col-sm-1">
							<img src="/static/images/excel.png" style={{opacity:0.5, width:"100%"}}></img>
						</div>

						{status}
					</div>
				</div>
			</div>
		)
	}

	render() {

		if (this.state.accepted.length > 0) {
			var acceptedFiles = this.state.accepted.map(f => this.generateFileView(f))
			return (
				<div className="row">
					<div className="col-lg-12">
						{acceptedFiles}
						<button className="btn btn-default" onClick={this.startOver.bind(this)} style={{marginRight: "5px", marginBottom: "20px"}}>START OVER & UPLOAD MORE</button>
					</div>
				</div>
			)
		}

		return (
			<div className="row" style={{marginBottom: "30px"}}>
				<div className="col-lg-12">
					<div className="dropzone">
						<Dropzone className="dropzone-component" activeClassName="dropzone-component-active" onDrop={this.onDrop.bind(this)} disabled={this.state.disabled}>
							<img src="/static/images/upload-icon.png" style={{opacity:0.5, width:"100px"}}></img>
							<h1 style={{marginBottom: "0px"}}>Drag & Drop</h1>
							<p style={{fontWeight: 600, color: "#aaa"}}>
								YOUR DESIGNS HERE
								<br />
							</p>
						</Dropzone>
					</div>
				</div>
			</div>
		);

	}
}
