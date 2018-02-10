import React from 'react';
import { BootstrapTable, TableHeaderColumn } from 'react-bootstrap-table';
import NewAssignmentModal from './NewAssignmentModal.jsx';

export default class AssignmentsTable extends React.Component {
    
    constructor(props) {
        super(props);
        this.state = {
            showNewAssignmentModal: false
        }
    }

    componentDidMount() {
    }

    statusFormatter(cell, row) {
        var status = row.status || "";
        var statusNode;
        if (status.toLocaleLowerCase() === "unassigned") {
            statusNode = <span className="label label-danger">{status}</span>
        } else if (status.toLocaleLowerCase() === "completed") {
            statusNode = <span className="label label-success">{status}</span>
        } else {
            statusNode = <span className="label label-warning">{status}</span>
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
            <small>{row.notes}</small>
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

        if (row.status.toLocaleLowerCase() === "completed") {
            return row.designer_username;      
        } else if (row.designer_username) {
            return (
                <div>
                    {row.designer_username}
                    <br />
                    <button className="btn btn-default btn-xs" style={{width:'90%', marginBottom:'5px'}} onClick={this.props.unassignDesigner.bind(null, row.id)}>UNASSIGN</button>
                </div>            
            )
        } else {
            return (
                <div>
                    <div className="input-group-btn">
                        <button className="btn btn-default dropdown-toggle" data-toggle="dropdown" type="button" style={{width:'100%'}}>
                        <span className="margin-right">Choose</span> 
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
        if (this.props.isDesignerView || row.status.toLocaleLowerCase() === "completed") {
            return (
                <div>
                    <a href={"/assignment/" + clientUsername + "/" + row.id}><button className="btn btn-primary btn-xs table-button">VIEW</button></a>
                </div>
            )        
        } else {

            return (
                <div>
                    <a href={"/assignment/" + clientUsername + "/" + row.id}><button className="btn btn-primary btn-xs table-button">VIEW</button></a>
                    <a href={"/assignment/" + clientUsername + "/" + row.id}><button className="btn btn-default btn-xs table-button">PING</button></a>
                    <a href={"/assignment/" + clientUsername + "/" + row.id}><button className="btn btn-default btn-xs table-button">DELETE</button></a>
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

    render() {
        let options = {
            defaultSortName: 'created_at',
            defaultSortOrder: 'desc'
        }

        var table;
        var newAssignmentBtn;
        if (this.props.isDesignerView) {
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

                    <TableHeaderColumn dataAlign="center" dataSort={true} dataField="status" editable={false} dataFormat={this.statusFormatter}>STATUS</TableHeaderColumn>
                    <TableHeaderColumn dataAlign="center" dataSort={true} dataField="created_at" editable={false} isKey={true}>CREATED ON</TableHeaderColumn>
                    <TableHeaderColumn dataAlign="center" dataSort={true} dataField="thumbnail" editable={false} dataFormat={this.inspirationFormatter}>INSPIRATION</TableHeaderColumn>
                    <TableHeaderColumn dataAlign="center" dataSort={true} dataField="notes" editable={false} dataFormat={this.notesFormatter}>NOTES</TableHeaderColumn>
                    <TableHeaderColumn dataAlign="center" dataSort={true} editable={false} dataFormat={this.actionsFormatter.bind(this)}>ACTIONS</TableHeaderColumn>

                </BootstrapTable>
            )
        } else {
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

                    <TableHeaderColumn dataAlign="center" dataSort={true} dataField="status" editable={false} dataFormat={this.statusFormatter}>STATUS</TableHeaderColumn>
                    <TableHeaderColumn dataAlign="center" dataSort={true} dataField="created_at" editable={false} isKey={true}>CREATED ON</TableHeaderColumn>
                    <TableHeaderColumn dataAlign="center" dataSort={true} dataField="thumbnail" editable={false} dataFormat={this.inspirationFormatter}>INSPIRATION</TableHeaderColumn>
                    <TableHeaderColumn dataAlign="center" dataSort={true} dataField="notes" editable={false} dataFormat={this.notesFormatter}>NOTES</TableHeaderColumn>
                    <TableHeaderColumn dataAlign="center" dataSort={true} dataField="designer_username" editable={false} dataFormat={this.designerFormatter.bind(this)}>DESIGNER</TableHeaderColumn>
                    <TableHeaderColumn dataAlign="center" dataSort={true} editable={false} dataFormat={this.actionsFormatter.bind(this)}>ACTIONS</TableHeaderColumn>

                </BootstrapTable>
            )        
            newAssignmentBtn = <button className="btn btn-primary" style={{marginLeft: '10px'}} onClick={this.showNewAssignmentModal.bind(this)}>NEW ASSIGNMENT</button>
        }


        return (
            <div className="hpanel">
                <NewAssignmentModal 
                    designers={this.props.designers} 
                    show={this.state.showNewAssignmentModal} 
                    onHide={this.onHideNewAssignmentModal.bind(this)} 
                    updateTable={this.props.updateTable} 
                />

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