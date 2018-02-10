import React from 'react';
import {NotificationContainer, NotificationManager} from 'react-notifications';

export default class NewDesignerPanel extends React.Component {
    
    addDesigner() {
        var designer_username = $("#designer-username").val();
        var rate = parseFloat($("#rate").val()) || 0;

        var designer = JSON.stringify({
            "designer_username": designer_username,
            "rate": rate
        });
        var data = {designer}
        $.post("/add_designer/", data, function(result) {
            var result = result;
            if (result !== "success") {
                NotificationManager.error('Error: ' + result);
            } else {
                NotificationManager.success('We successfully added your new designer!');            
                designer = JSON.parse(designer);
                designer.unpaid_commissions = 0;
                designer.pending_commissions = 0;
                designer.status_breakdown = {};
                designer.assigned_on = new Date().toISOString();
                designer.actual_hours = 0;
                designer.designs_uploaded = 0;

                this.props.updateTable(designer);
            }


        }.bind(this));
    }

    render() {
        return (
            <div className="hpanel">
                <NotificationContainer/>
                <div className="panel-heading hbuilt">
                    <div className="panel-tools">
                        <a className="showhide"><i className="fa fa-chevron-up"></i></a>
                    </div>
                    <span style={{marginLeft:'10px'}}>New Assignment</span>
                </div>
                <div className="panel-body" style={{textAlign:'left'}}>
                    <div className="form-group"><label className="control-label">Designer Username</label>
                        <input type="text" className="form-control input-sm" id="designer-username"></input>
                    </div>
                    <div className="form-group"><label className="control-label">Rate</label>
                        <input type="text" className="form-control input-sm" id="rate"></input>
                    </div>
                    <div className="text-center">
                        <button className="btn btn-success" style={{fontWeight:300, fontFamily: 'Open Sans'}} onClick={this.addDesigner.bind(this)}>ADD DESIGNER</button>
                    </div>
                </div>
            </div>
        )
    }
}