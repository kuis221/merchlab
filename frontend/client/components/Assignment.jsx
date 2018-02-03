import React from 'react';
import DesignUploader from './DesignUploader.jsx'
import ProductVisualizer from './ProductVisualizer.jsx'
import request from 'superagent';

export default class Assignment extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loaded: false,
            assignment: {}
        }
    }

    componentDidMount() {
        var assignment_id = $("#assignment-id").text();

        this.serverRequest = $.get('/assignment/' + assignment_id + '/data/', function (result) {
            var assignment = JSON.parse(result);
            console.log(assignment);
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

        var designs_array = [];
        for (var key in this.state.assignment.completed_work || {}) {
            var design = this.state.assignment.completed_work[key]
            design.id = key;
            designs_array.push(design);
        }

        var assignment = this.state.assignment;
        console.log("rendering design nodes");
        var image_nodes = designs_array.map(function(design) {
            console.log("design", design);
            var url = design.s3_url;
            return (
                <div className="col-lg-6 text-center design-image-div">
                    <img src={url} className="design-image" style={{maxWidth:"100%", height:'200px', marginBottom:'10px'}}></img>
                    <br />
                    <button className="btn btn-sm btn-primary">APPROVE</button>
                </div>)
        })

        var num_uploaded = Object.keys(this.state.assignment.completed_work || {}).length;
        var raw_completed_percent = (num_uploaded * 100 / assignment.num_variations) || 0;
        var completed_percent = Math.min(100, raw_completed_percent);
        var completed_percent_color = "text-warning";
        if (completed_percent === 0) {
            completed_percent_color = "text-danger";
        } else if (completed_percent === 100) {
            completed_percent_color = "text-success";            
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
                                    <span className="margin-right">Unapproved</span> 
                                    <span className="caret"></span></button>
                                    <ul className="dropdown-menu dropdown-menu-left" style={{marginTop:'17.5px'}}>
                                        <li><a href="#a">Unapproved</a></li>
                                        <li><a href="#a">Approved</a></li>
                                    </ul>
                                </div>                                
                                <button className="btn btn-success btn-sm pull-right">COMPLETE ASSIGNMENT</button>
                                <button className="btn btn-default btn-sm margin-right pull-right">EXPORT DESIGNS</button>
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
                                    <div className="panel-body list" style={{height:'280px', overflow: 'scroll'}}>
                                        <div className="stats-title pull-left">
                                            <h4>Assignment Details</h4>
                                        </div>
                                        <div className="m-t-xl">
                                            <p>
                                                <label>Designer:</label> {assignment.designer_username}
                                                <button className="btn btn-xs btn-default" style={{marginLeft:'5px'}}>Unassign</button>
                                            </p>
                                            <p>
                                                <label>Rate:</label> ${assignment.rate}
                                            </p>
                                            <p>
                                                <label>Estimated Hours:</label> {assignment.estimated_hours}
                                            </p>
                                            <p>
                                                <label># Variations:</label> {assignment.num_variations} (<small className={completed_percent_color}><strong>{completed_percent}% complete!</strong></small>)
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