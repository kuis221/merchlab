import React from 'react';
import { Modal, OverlayTrigger, Popover, Button, 
    FormGroup, FormControl, ControlLabel, Alert } from 'react-bootstrap';
import { LineChart, Line, CartesianGrid, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';
import { BootstrapTable, TableHeaderColumn } from 'react-bootstrap-table';

export default class UploadedDesignsVisualizer extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            loaded: false,  
            completed_work_display: "all"          
        }
    }

    approveDesign(id) {
        var assignmentId = this.props.assignmentId;
        var data = {
            "upload_uuid": id
        }
        this.serverRequest = $.post('/assignment/' + assignmentId + '/approve/', data, function (result) {
            var assignment = this.state.assignment;
            var completed_work = assignment.completed_work;
            completed_work[id].approved = true;
            assignment.completed_work = completed_work;

            this.setState({
                assignment: assignment,
                loaded: true
            });
        }.bind(this));   
    }

    disapproveDesign(id) {
        var assignmentId = this.props.assignmentId;
        var data = {
            "upload_uuid": id
        }
        this.serverRequest = $.post('/assignment/' + assignment_id + '/disapprove/', data, function (result) {
            var assignment = this.state.assignment;
            var completed_work = assignment.completed_work;
            completed_work[id].approved = false;
            assignment.completed_work = completed_work;

            this.setState({
                assignment: assignment,
                loaded: true
            });
        }.bind(this));   
    }

    render() {
        console.log("hehehe this is assignment", this.props.assignment);
        var assignment = this.props.assignment || {};
        var designs_array = [];
        for (var key in assignment.completed_work || {}) {
            var design = assignment.completed_work[key]
            design.id = key;
            designs_array.push(design);
        }
        var image_nodes;
        if (designs_array.length === 0) {
            
            if (this.state.isDesigner) {
                image_nodes = (
                    <div>
                        <p>You have not uploaded any designs. Drag and drop above to upload some designs!</p>
                    </div>
                )
            } else {
                image_nodes = (
                    <div>
                        <p>Your designer has not uploaded any designs for this assignment.</p>
                        <button className="btn btn-primary btn-sm">PING DESIGNER FOR UPDATES</button>
                    </div>
                )
            }
        } else {
            var completed_work_display = this.state.completed_work_display;
            if (completed_work_display === "unapproved") {
                designs_array = designs_array.filter(design => design.approved !== true)
            } else if  (completed_work_display === "approved") {
                designs_array = designs_array.filter(design => design.approved === true)
            }

            if (designs_array.length === 0) {
                var image_nodes = (
                    <div>
                        <p>There are no designs for you to view in this tab.</p>
                    </div>
                )
            } else {
                console.log("rendering design nodes");
                image_nodes = designs_array.map(function(design) {
                    console.log("design", design);
                    var url = design.s3_url;
                    var btn;
                    if (!design.approved) {
                        btn = <button className="btn btn-sm btn-primary" onClick={this.approveDesign.bind(this, design.id)}>APPROVE</button>
                    } else {
                        btn = <button className="btn btn-sm btn-danger" onClick={this.disapproveDesign.bind(this, design.id)}>DISAPPROVE</button>                    
                    }
                    return (
                        <div className="col-lg-4 text-center design-image-div">
                            <img src={url} className="design-image" style={{maxWidth:"100%", height:'150px', marginBottom:'10px'}}></img>
                            <br />
                            {btn}
                        </div>)
                }.bind(this))            
            }
        }

        var completeAssignmentButton; 
        if (assignment.status !== "completed") {
            completeAssignmentButton = (
                <button className="btn btn-success btn-sm pull-right">COMPLETE ASSIGNMENT</button>
            )
        }        

        return (
	        <Modal show={this.props.show} onHide={this.props.onHide} bsSize="lg">
	            <Modal.Header closeButton>
	                <h4 className="modal-title" style={{fontWeight:300, fontFamily:'Open Sans'}}>Design(s) For Review</h4>


	            </Modal.Header>
	            <Modal.Body>
	                <div className="row">
	                    <div className="col-lg-12">
                            <label style={{marginRight:'5px'}}>Viewing: </label>
                            <div className="input-group-btn margin-right" style={{display:'inline'}}>
                                <button className="btn btn-default dropdown-toggle" data-toggle="dropdown" type="button">
                                <span className="margin-right">{this.state.completed_work_display}</span> 
                                <span className="caret"></span></button>
                                <ul className="dropdown-menu dropdown-menu-left" style={{marginTop:'17.5px'}}>
                                    <li><a href="#a" onClick={this.setState.bind(this, {completed_work_display: 'all'})}>all</a></li>
                                    <li><a href="#a" onClick={this.setState.bind(this, {completed_work_display: 'unapproved'})}>unapproved</a></li>
                                    <li><a href="#a" onClick={this.setState.bind(this, {completed_work_display: 'approved'})}>approved</a></li>
                                </ul>
                            </div>                                
                            {completeAssignmentButton}
                            <button className="btn btn-default btn-sm margin-right pull-right">DOWNLOAD DESIGNS (.ZIP)</button>
                            <hr /><br />
                            {image_nodes}
                        </div>
	                </div>
	            </Modal.Body>
	        </Modal>
        )
	}

}