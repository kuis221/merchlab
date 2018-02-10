import React from 'react';
import DesignUploader from './DesignUploader.jsx'
import ProductVisualizer from './ProductVisualizer.jsx'
import request from 'superagent';

export default class Assignment extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loaded: false,
            assignment: {},
            completed_work_display: "all",
            isDesigner: false
        }
    }

    componentDidMount() {
        var assignment_id = $("#assignment-id").text();
        var client_username = $("#client-username").text();
        this.serverRequest = $.get('/assignment/' + client_username + '/' + assignment_id + '/data/', function (result) {
            var result = JSON.parse(result);
            var assignment = result.assignment;
            var isDesigner = result.is_designer;
            var designers = result.designers; // this field won't exist if user is designer
            console.log(assignment);
            this.setState({
                assignment: assignment,
                loaded: true,
                isDesigner: isDesigner,
                designers: designers
            });
        }.bind(this));    
    }

    approveDesign(id) {
        var assignment_id = $("#assignment-id").text();
        var data = {
            "upload_uuid": id
        }
        this.serverRequest = $.post('/assignment/' + assignment_id + '/approve/', data, function (result) {
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
        var assignment_id = $("#assignment-id").text();
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

    updateDesignerUploads(id, design_data) {
        var assignment = this.state.assignment;
        var completed_work = assignment.completed_work || {};
        completed_work[id] = design_data;
        assignment.completed_work = completed_work;
        this.setState({assignment});
    }

    assignDesigner(designerUsername) {
        var assignment = this.state.assignment;
        assignment.designer_username = designerUsername;
        assignment.status = "assigned"

        var data = {
            designer_username: designerUsername,
            assignment_id: $("#assignment-id").text(),
            client_username: $("#client-username").text()
        }

        this.serverRequest = $.post('/assign_designer_to_assignment/', data, function (result) {
            var data = JSON.parse(result);
            console.log(data);
        }.bind(this));    

        this.setState({assignment})
    }

    unassignDesigner() {
        var assignment = this.state.assignment;
        assignment.designer_username = null;
        assignment.status = "unassigned"

        var data = {
            assignment_id: $("#assignment-id").text(),
            client_username: $("#client-username").text()
        }

        this.serverRequest = $.post('/unassign_designer_from_assignment/', data, function (result) {
            var data = JSON.parse(result);
            console.log(data);
        }.bind(this));    


        this.setState({assignment})
    }

    completeAssignment() {
        var assignment = this.state.assignment;
        assignment.status = "completed"
        assignment.actual_hours = 10000000

        var data = {
            assignment_id: $("#assignment-id").text(),
            client_username: $("#client-username").text(),
            actual_hours: 10000000
        }

        this.serverRequest = $.post('/complete_assignment/', data, function (result) {
            var data = JSON.parse(result);
            console.log(data);
        }.bind(this));    


        this.setState({assignment})    
    }

    showModal(assignment) {
        this.setState({
            showModal: true
        })

        var req = request
            .get('/product_metadata/' + assignment.asin)
            .end(function(err, res) {
                console.log(res.text)
                this.setState({
                    loaded: true,
                    productData: JSON.parse(res.text),
                    selectedProduct: {image: assignment.thumbnail}
                })
            }.bind(this));

    }
    closeModal() {

        console.log("hit here");
        this.setState({
            showModal: false
        })
    }

    render() {
        var assignment_id = $("#assignment-id").text();
        var assignment = this.state.assignment;

        var designs_array = [];
        for (var key in this.state.assignment.completed_work || {}) {
            var design = this.state.assignment.completed_work[key]
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
                        <div className="col-lg-6 text-center design-image-div">
                            <img src={url} className="design-image" style={{maxWidth:"100%", height:'200px', marginBottom:'10px'}}></img>
                            <br />
                            {btn}
                        </div>)
                }.bind(this))            
            }
        }


        var num_uploaded = Object.keys(this.state.assignment.completed_work || {}).length;
        var raw_completed_percent = (num_uploaded * 100 / assignment.num_variations) || 0;
        var completed_percent = Math.min(100, raw_completed_percent);
        var completed_percent_color = "text-warning";
        if (completed_percent === 0) {
            completed_percent_color = "text-danger";
        } else if (completed_percent === 100) {
            completed_percent_color = "text-success";            
        }

        var designerInfo;

        if (!this.state.isDesigner) {
            if (this.state.assignment.designer_username) {
                if (this.state.assignment.status.toLocaleLowerCase() !== "completed") {
                    designerInfo = (
                        <p>
                            <label>Designer:</label> {assignment.designer_username}
                            <button className="btn btn-xs btn-default" style={{marginLeft:'5px'}} onClick={this.unassignDesigner.bind(this)}>Unassign</button>
                        </p>
                    )        
                } else {
                    designerInfo = (
                        <p>
                            <label>Designer:</label> {assignment.designer_username}
                        </p>
                    )                     
                }
        

            } else {

                var designers = this.state.designers || [];
                var designerNames = [];
                for (var c=0; c<designers.length;c++) {
                    designerNames.push(designers[c].designer_username)
                }
                var designerNodes = designerNames.map(function(name) {
                    return (
                        <li><a href="#a" onClick={this.assignDesigner.bind(this, name)}>{name}</a></li>
                    )
                }.bind(this));

                designerInfo = (
                    <div>
                        <label>Designer:</label>
                        <div className="input-group-btn">
                            <button className="btn btn-default btn-sm dropdown-toggle" data-toggle="dropdown" type="button" style={{width:'100%'}}>
                            <span className="margin-right">Choose</span> 
                            <span className="caret"></span></button>
                            <ul className="dropdown-menu dropdown-menu-left">
                                {designerNodes}
                            </ul>
                        </div>
                        <br />
                    </div>
                )        
            }
        } else {
            designerInfo = <p><label>Designer:</label> {assignment.designer_username}</p>
        }

        var completeAssignmentButton; 
        if (this.state.assignment.status !== "completed") {
            completeAssignmentButton = (
                <button className="btn btn-success btn-sm pull-right" onClick={this.completeAssignment.bind(this)}>COMPLETE ASSIGNMENT</button>
            )
        }        

        return (
            <div className="content">
                <div className="row">
                    <div className="col-lg-8">
                        <div className="hpanel">
                            <div className="panel-heading hbuilt">
                                <span style={{marginLeft:'10px'}}>Assignment Progress</span>
                            </div>
                            <div className="panel-body">
                                <div className="text-center" style={{marginBottom: '10px'}}>
                                    <DesignUploader update={this.updateDesignerUploads.bind(this)} assignment_id={assignment_id} />
                                </div>
                                <h4>Previously Completed Work</h4>
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
                    </div>

                    <div className="col-lg-4">
                        <div className="row">
                            <div className="col-lg-12">
                                <ProductVisualizer 
                                    show={this.state.showModal} productData={this.state.productData} 
                                    selectedProduct={this.state.selectedProduct} onHide={this.closeModal.bind(this)}>
                                </ProductVisualizer>
                                <a href="#a" onClick={this.showModal.bind(this, assignment)}>
                                <div className="hpanel">
                                    <div className="panel-body text-center" style={{height:'280px'}}>
                                        <div className="stats-title pull-left">
                                            <h4>Inspiration</h4>
                                        </div>
                                        <br /><br/>
                                        <img src={assignment.thumbnail} style={{height: '200px'}}></img>
                                    </div>
                                </div></a>
                            </div>
                            <div className="col-lg-12">
                                <div className="hpanel stats">
                                    <div className="panel-body list">
                                        <div className="stats-title pull-left">
                                            <h4>Assignment Details</h4>
                                        </div>
                                        <div className="m-t-xl">
                                            {designerInfo}
                                            <p>
                                                <label>Status:</label> {assignment.status}
                                            </p>
                                            <p>
                                                <label>Rate:</label> ${assignment.rate}
                                            </p>
                                            <p>
                                                <label>Estimated Hours:</label> {assignment.estimated_hours}
                                            </p>
                                            <p>
                                                <label>Actual Hours:</label> {assignment.actual_hours || "N/A"}
                                            </p>
                                            <p>
                                                <label># Variations:</label> {assignment.num_variations} (<small className={completed_percent_color}><strong>{parseInt(completed_percent)}% complete!</strong></small>)
                                            </p>
                                            <p>
                                                <label>Notes:</label> {assignment.notes}
                                            </p>
                                        </div>
                                    </div>
                                    <br />
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        )
    }
}