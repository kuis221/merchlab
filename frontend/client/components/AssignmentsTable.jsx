import React from 'react';
import { BootstrapTable, TableHeaderColumn } from 'react-bootstrap-table';
import NewAssignmentModal from './NewAssignmentModal.jsx';
import UploadedDesignsVisualizer from './UploadedDesignsVisualizer.jsx';

export default class AssignmentsTable extends React.Component {
    
    constructor(props) {
        super(props);
        this.state = {
            showNewAssignmentModal: false,
            showUploadedDesignsVisualizer: false
        }
    }

    componentDidMount() {
    }

    statusFormatter(cell, row) {
        var status = row.status || "";
        var statusNode;
        if (status.toLocaleLowerCase() === "unassigned") {
            statusNode = <span className="label label-danger" style={{fontWeight: 400, fontSize:'13px'}}>{status}</span>
        } else if (status.toLocaleLowerCase() === "completed") {
            statusNode = <span className="label label-success" style={{fontWeight: 400, fontSize:'13px'}}>{status}</span>
        } else {
            statusNode = <span className="label label-warning" style={{fontWeight: 400, fontSize:'13px'}}>{status}</span>
        }
        return statusNode;
    }

    inspirationFormatter(cell, row) {
        if (row.thumbnail) {
            return (
                <img src={row.thumbnail || ""} style={{height:'100px'}}></img>
            )        
        } else {
            return (
                <div>
                    {row.asin}
                    <br/><small>(Image not found)</small>
                </div>
            )
        }

    }

    notesFormatter(cell, row) {
        return (
            <div className="text-left">{row.notes}</div>
        )
    }


    designerFormatter(cell, row) {
        var designers = this.props.designers;
        var designerNames = [];
        for (var c=0; c<designers.length;c++) {
            designerNames.push(designers[c].designer_username)
        }
        var designerNodes = designerNames.map(function(name) {
            return (
                <li><a href="#a" onClick={this.props.assignDesigner.bind(null, row.id, name)}>{name}</a></li>
            )
        }.bind(this));

        if (!row.status) {
            row.status = "unassigned";
        }
        if (row.status.toLocaleLowerCase() === "completed") {
            return row.designer_username;      
        } else {
            return (
                <div>
                    <div className="input-group-btn">
                        <button className="btn btn-default dropdown-toggle" data-toggle="dropdown" type="button" style={{width:'100%'}}>
                        <span className="margin-right">{row.designer_username || "Choose"}</span> 
                        <span className="caret"></span></button>
                        <ul className="dropdown-menu dropdown-menu-left">
                            {designerNodes}
                        </ul>
                    </div>
                </div>
            )        
        }
    }


    actionsFormatter(cell, row) {
        var clientUsername = $("#client-username").text();
        if (this.props.isDesignerView) {
            return (
                <div>
                    <a href={"/assignment/" + clientUsername + "/" + row.id}><button className="btn btn-primary btn-xs table-button">VIEW</button></a>
                </div>
            )        
        } else {
            var deleteButton;
            if (row.status.toLocaleLowerCase() !== "completed") {
                deleteButton = <a href={"/assignment/" + clientUsername + "/" + row.id}><button className="btn btn-default btn-xs table-button">DELETE</button></a>;
            }

            return (
                <div>
                    <a href="#a" onClick={this.showUploadedDesignsVisualizer.bind(this, row.id)}><button className="btn btn-primary btn-xs table-button">VIEW</button></a>
                    {deleteButton}
                </div>
            )        
        }

    }

    showNewAssignmentModal() {
        this.setState({
            showNewAssignmentModal: true
        })
    }

    onHideNewAssignmentModal() {
        this.setState({
            showNewAssignmentModal: false
        })
    }

    showUploadedDesignsVisualizer(assignmentId) {
        var client_username = $("#client-username").text();
        this.serverRequest = $.get('/assignment/' + client_username + '/' + assignmentId + '/data/', function (result) {
            var result = JSON.parse(result);
            var assignment = result.assignment;
            var isDesigner = result.is_designer;
            var designers = result.designers; // this field won't exist if user is designer
            console.log(assignment);
            this.setState({
                assignment: assignment,
                assignmentId: assignmentId,
                showUploadedDesignsVisualizer: true
            });
        }.bind(this));
    }

    onHideUploadedDesignsVisualizer() {
        this.setState({
            showUploadedDesignsVisualizer: false
        })
    }
    dateFormatter(cell, row) {
        console.log("hello")
        var date = new Date(cell);
        var options = { year: 'numeric', month: 'long', day: 'numeric' };
        date = date.toLocaleDateString("en-US",options);

        var status = this.statusFormatter(cell, row);
        return (
            <div style={{marginBottom: '10px'}}>
                <div style={{marginBottom: '10px'}}>{date}</div>
                {status}
            </div>
        )
    }

    quantityFormatter(cell, row) {
        var completed_work = row.completed_work || {};
        return Object.keys(completed_work).length + "/" + cell +  " uploaded"
    }

    render() {
        let options = {
            defaultSortName: 'created_at',
            defaultSortOrder: 'desc'
        }

        var table;
        var newAssignmentBtn;


        var designerColumn;

        if (!this.props.isDesignerView) {
            designerColumn = (<TableHeaderColumn dataAlign="center" dataSort={true} dataField="designer_username" editable={false} dataFormat={this.designerFormatter.bind(this)}>DESIGNER</TableHeaderColumn>);
            newAssignmentBtn = <button className="btn btn-primary" style={{marginLeft: '10px'}} onClick={this.showNewAssignmentModal.bind(this)}>NEW ASSIGNMENT</button>            
        }

        table = (
            <BootstrapTable
                    data={this.props.assignments} 
                    exportCSV={false} 
                    striped={false} 
                    bordered={false} 
                    hover={false} 
                    pagination={true}
                    search={true}
                    options={options}
                >
                {designerColumn}
                <TableHeaderColumn dataAlign="center" dataSort={true} dataField="created_at" editable={false} isKey={true} dataFormat={this.dateFormatter.bind(this)} >CREATED ON</TableHeaderColumn>
                <TableHeaderColumn dataAlign="center" dataSort={true} dataField="thumbnail" editable={false} dataFormat={this.inspirationFormatter}>INSPIRATION</TableHeaderColumn>
                <TableHeaderColumn dataAlign="center" dataSort={true} dataField="notes" editable={false} dataFormat={this.notesFormatter}>NOTES</TableHeaderColumn>
                <TableHeaderColumn dataAlign="center" dataSort={true} dataField="num_variations" editable={false} dataFormat={this.quantityFormatter}>QUANTITY</TableHeaderColumn>
                <TableHeaderColumn dataAlign="center" dataSort={true} dataField="gender" editable={false}>GENDER</TableHeaderColumn>
                <TableHeaderColumn dataAlign="center" dataSort={true} dataField="niche" editable={false}>NICHE</TableHeaderColumn>

                <TableHeaderColumn dataAlign="center" dataSort={true} editable={false} dataFormat={this.actionsFormatter.bind(this)} width='12%'>ACTIONS</TableHeaderColumn>

            </BootstrapTable>
        )        


        return (
            <div className="hpanel">
                <NewAssignmentModal 
                    designers={this.props.designers} 
                    show={this.state.showNewAssignmentModal} 
                    onHide={this.onHideNewAssignmentModal.bind(this)} 
                    updateTable={this.props.updateTable} 
                />
                <UploadedDesignsVisualizer assignment={this.state.assignment} show={this.state.showUploadedDesignsVisualizer} onHide={this.onHideUploadedDesignsVisualizer.bind(this)} />

                <div className="panel-heading hbuilt">
                    <div className="panel-tools">
                        <a className="showhide"><i className="fa fa-chevron-up"></i></a>
                    </div>
                    <span style={{marginLeft:'10px'}}>Assignments</span>
                </div>
                <div className="panel-body">
                    <div className="row ">
                        <div className="col-lg-12 text-left">
                            <label style={{marginRight:'5px'}}>Currently Viewing: </label>
                            <div className="input-group-btn" style={{display:'inline'}}>
                                <button className="btn btn-default dropdown-toggle" data-toggle="dropdown" type="button">
                                <span className="margin-right">Unassigned Assignments</span> 
                                <span className="caret"></span></button>
                                <ul className="dropdown-menu dropdown-menu-left" style={{marginTop:'17.5px'}}>
                                    <li><a href="#a">Complete</a></li>
                                    <li><a href="#a">Assigned</a></li>
                                    <li><a href="#a">Unassigned</a></li>
                                    <li><a href="#a">In Progress</a></li>
                                    <li><a href="#a">Deleted</a></li>
                                </ul>
                            </div>
                            {newAssignmentBtn}
                            <br />
                            {table}
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}