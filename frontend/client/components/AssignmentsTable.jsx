import React from 'react';
import { BootstrapTable, TableHeaderColumn } from 'react-bootstrap-table';

export default class AssignmentsTable extends React.Component {
    
    constructor(props) {
        super(props);
    }

    componentDidMount() {
    }

    statusFormatter(cell, row) {
        var status = row.status || "";
        var statusNode;
        if (status.toLocaleLowerCase() === "unassigned") {
            statusNode = <span className="label label-danger">{status}</span>
        } else if (status.toLocaleLowerCase() === "complete") {
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
        if (row.designer_username) {
            return (
                <div>
                    {row.designer_username}
                    <br />
                    <button className="btn btn-default btn-xs" style={{width:'90%', marginBottom:'5px'}}>UNASSIGN</button>
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
                            <li><a href="#a">Adrian</a></li>
                            <li><a href="#a">Bob</a></li>
                            <li><a href="#a">Joe</a></li>
                            <li><a href="#a">Jim</a></li>
                        </ul>
                    </div>
                </div>
            )        
        }
    }

    actionsFormatter(cell, row) {
        return (
            <div>
                <a href={"/assignment/" + row.id}><button className="btn btn-primary btn-xs table-button">VIEW</button></a>
                <button className="btn btn-default btn-xs table-button">PING</button>
                <button className="btn btn-default btn-xs table-button">DELETE</button>

            </div>
        )
    }

    render() {
        var table = (
            <BootstrapTable
                    data={this.props.assignments} 
                    exportCSV={false} 
                    striped={false} 
                    bordered={false} 
                    hover={false} 
                    pagination={true}
                    search={true}
                >

                <TableHeaderColumn dataAlign="center" dataSort={true} dataField="status" editable={false} dataFormat={this.statusFormatter}>STATUS</TableHeaderColumn>
                <TableHeaderColumn dataAlign="center" dataSort={true} dataField="created_at" editable={false}>CREATED ON</TableHeaderColumn>
                <TableHeaderColumn dataAlign="center" dataSort={true} dataField="thumbnail" editable={false} dataFormat={this.inspirationFormatter}>INSPIRATION</TableHeaderColumn>
                <TableHeaderColumn dataAlign="center" dataSort={true} dataField="notes" editable={false} dataFormat={this.notesFormatter}>NOTES</TableHeaderColumn>
                <TableHeaderColumn dataAlign="center" dataSort={true} dataField="designer_username" editable={false} dataFormat={this.designerFormatter} isKey={true}>DESIGNER</TableHeaderColumn>
                <TableHeaderColumn dataAlign="center" dataSort={true} editable={false} dataFormat={this.actionsFormatter}>ACTIONS</TableHeaderColumn>

            </BootstrapTable>
        )

        return (
        <div className="hpanel">
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
                        <div className="btn btn-primary" style={{marginLeft: '10px'}} >NEW ASSIGNMENT</div>
                        <br />
                        {table}
                    </div>
                </div>
            </div>
        </div>
        )
    }
}