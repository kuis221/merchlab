import React from 'react';
import { Modal, OverlayTrigger, Popover, Button, 
    FormGroup, FormControl, ControlLabel, Alert } from 'react-bootstrap';


export default class CompleteAssignmentModal extends React.Component {
    
    constructor(props) {
        super(props);
        this.state = {

        }
    }

    completeAssignment() {
        var data = {
            actual_hours: $("#actual-hours").val()
        }
        var data = {assignment}
        $.post("/completeAssignment/", data, function(result) {
            ("#actual-hours").val("");
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
                    <h4 className="modal-title" style={{fontWeight:300, fontFamily:'Open Sans'}}>Complete Assignment</h4>
                </Modal.Header>
                <Modal.Body>
                    <div className="form-group"><label className="control-label">Actual Hours</label>
                        <input type="text" className="form-control input-sm" id="actual-hours"></input>
                    </div>
                    <div className="text-center">
                        <button className="btn btn-success" style={{fontWeight:300, fontFamily: 'Open Sans'}} onClick={this.completeAssignment.bind(this)}>COMPLETE ASSIGNMENT</button>
                    </div>                
                </Modal.Body>
            </Modal>
        )
    }
}