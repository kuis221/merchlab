import React from 'react';

export default class NewAssignmentPanel extends React.Component {
    
    addAssignment() {
        var designer_username = $("#designer-username").val();
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
            assignment = JSON.parse(assignment)
            assignment.id = result.name;
            this.props.updateTable(assignment);
            $("#designer-username").val("");
            $("#asin").val("");
            $("#rate").val("");
            $("#estimated-hours").val("");
            $("#num-variations").val("");
            $("#notes").val("");
        }.bind(this));
    }

    render() {
        return (
            <div className="hpanel">
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
                    <div className="form-group"><label className="control-label">ASIN</label>
                        <input type="text" className="form-control input-sm" id="asin"></input>
                    </div>
                    <div className="form-group"><label className="control-label">Rate</label>
                        <input type="text" className="form-control input-sm" id="rate"></input>
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
                </div>
            </div>
        )
    }
}