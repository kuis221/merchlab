import React from 'react';
import { Modal, OverlayTrigger, Popover, Button, 
    FormGroup, FormControl, ControlLabel, Alert } from 'react-bootstrap';


export default class NewAssignmentModal extends React.Component {
    
    constructor(props) {
        super(props);
        this.state = {

        }
    }

    addAssignment() {
        var designer_username = this.state.designer;
        var asin = $("#asin").val();
        var rate = parseFloat($("#rate").val()) || 0;
        var estimated_hours = parseInt($("#estimated-hours").val()) || 0;
        var num_variations = parseInt($("#num-variations").val()) || 0;
        var notes = $("#notes").val();
        var assignment = JSON.stringify({
            designer_username: designer_username,
            asin: asin,
            rate: rate,
            estimated_hours: estimated_hours, 
            num_variations: num_variations,
            status: "assigned",
            notes: notes
        })
        var data = {assignment}
        $.post("/add_assignment/", data, function(result) {
            console.log(result);
            console.log(this);
            result = JSON.parse(result);
            assignment = JSON.parse(assignment)
            assignment.id = result.name;
            assignment.created_at = new Date().toISOString();
            this.props.updateTable(assignment);
            $("#asin").val("");
            $("#rate").val("");
            $("#estimated-hours").val("");
            $("#num-variations").val("");
            $("#notes").val("");
            this.setState({designer:null});
            this.props.onHide();
        }.bind(this));
    }

    assignDesigner(designer, rate) {
        this.setState({designer, rate})
        $("#rate").val(rate);
    }

    render() {

        var designerNodes = (this.props.designers || []).map(function(designer) {
            return (
                <li><a href="#a" onClick={this.assignDesigner.bind(this, designer.designer_username, designer.rate)}>{designer.designer_username}</a></li>
            )
        }.bind(this));

        var chooseDesignerNode = (
            <div>
                <div className="input-group-btn">
                    <button className="btn btn-default dropdown-toggle" data-toggle="dropdown" type="button" style={{width:'100%'}}>
                    <span className="margin-right">{this.state.designer || "Choose"}</span> 
                    <span className="caret"></span></button>
                    <ul className="dropdown-menu dropdown-menu-left">
                        {designerNodes}
                    </ul>
                </div>
            </div>
        )        

        return (
            <Modal show={this.props.show} onHide={this.props.onHide}>
                <Modal.Header closeButton>
                    <h4 className="modal-title" style={{fontWeight:300, fontFamily:'Open Sans'}}>New Assignment</h4>
                </Modal.Header>
                <Modal.Body>
                    <div className="form-group"><label className="control-label">Designer Username</label>
                        {chooseDesignerNode}
                    </div>
                    <div className="form-group"><label className="control-label">Rate</label>
                        <input type="text" className="form-control input-sm" id="rate"></input>
                    </div>

                    <div className="form-group"><label className="control-label">ASIN</label>
                        <input type="text" className="form-control input-sm" id="asin"></input>
                    </div>

                    <div className="form-group"><label className="control-label">Estimated Hours</label>
                        <input type="text" className="form-control input-sm" id="estimated-hours"></input>
                    </div>
                    <div className="form-group"><label className="control-label"># Variations</label>
                        <input type="text" className="form-control input-sm" id="num-variations"></input>
                    </div>
                    <div className="form-group"><label className="control-label">Notes</label>
                        <textarea type="text" className="form-control input-sm" id="notes"></textarea>
                    </div>
                    <div className="text-center">
                        <button className="btn btn-success" style={{fontWeight:300, fontFamily: 'Open Sans'}} onClick={this.addAssignment.bind(this)}>ADD ASSIGNMENT</button>
                    </div>                
                </Modal.Body>
            </Modal>
        )
    }
}