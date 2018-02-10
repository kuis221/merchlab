import React from 'react';
import { BootstrapTable, TableHeaderColumn } from 'react-bootstrap-table';
import NewDesignerModal from './NewDesignerModal.jsx';

export default class DesignersTable extends React.Component {
    
    constructor(props) {
        super(props);
        this.state = {
            showNewDesignerModal: false
        }
    }

    componentDidMount() {
    }

    actionsFormatter(cell, row) {
        return (
            <div>
                <button className="btn btn-primary btn-xs table-button">GENERATE PAYOUT</button>
                <button className="btn btn-default btn-xs table-button" onClick={this.props.unassignDesignerFromClient.bind(null, row.designer_username)}>REMOVE</button>

            </div>
        )
    }

    showNewDesignerModal() {
        this.setState({
            showNewDesignerModal: true
        })
    }

    onHideNewDesignerModal() {
        this.setState({
            showNewDesignerModal: false
        })
    }

    formatStatusBreakdown(cell, row) {
        var statusBreakdown = cell;
        console.log(cell)
        var nodes = Object.keys(statusBreakdown || {}).map(function(status) {
            return <div>{status}: {statusBreakdown[status]}</div>
        })
        return <div>{nodes}</div>
    }

    render() {
        var table = (
            <BootstrapTable
                    data={this.props.designers} 
                    exportCSV={false} 
                    striped={false} 
                    bordered={false} 
                    hover={false} 
                    pagination={true}
                    search={false}
                >
                <TableHeaderColumn dataAlign="center" dataSort={true} dataField="designer_username" editable={false} isKey={true}>DESIGNER NAME</TableHeaderColumn>
                <TableHeaderColumn dataAlign="center" dataSort={true} dataField="assigned_on" editable={false}>ADDED ON</TableHeaderColumn>
                <TableHeaderColumn dataAlign="center" dataSort={true} dataField="rate" editable={false}>RATE</TableHeaderColumn>
                <TableHeaderColumn dataAlign="center" dataSort={true} dataField="approved_commission_amount" editable={false}>APPROVED</TableHeaderColumn>
                <TableHeaderColumn dataAlign="center" dataSort={true} dataField="unapproved_commission_amount" editable={false}>UNAPPROVED</TableHeaderColumn>
                <TableHeaderColumn dataAlign="center" dataSort={true} dataField="status_breakdown" editable={false} dataFormat={this.formatStatusBreakdown}>ASSIGNMENTS</TableHeaderColumn>
                <TableHeaderColumn dataAlign="center" dataSort={false} editable={false} dataFormat={this.actionsFormatter.bind(this)}>ACTIONS</TableHeaderColumn>

            </BootstrapTable>
        )

        return (
        <div className="hpanel">
            <NewDesignerModal updateTable={this.props.updateTable} show={this.state.showNewDesignerModal} onHide={this.onHideNewDesignerModal.bind(this)} />

            <div className="panel-heading hbuilt">
                <div className="panel-tools">
                    <a className="showhide"><i className="fa fa-chevron-up"></i></a>
                </div>
                <span style={{marginLeft:'10px'}}>Designers</span>
            </div>
            <div className="panel-body">
                <div className="row ">
                    <div className="col-lg-12 text-left">
                        <div className="btn btn-primary btn-sm" style={{marginLeft: '10px'}} onClick={this.showNewDesignerModal.bind(this)} >NEW DESIGNER</div>
                        <br />
                        {table}
                    </div>
                </div>
            </div>
        </div>
        )
    }
}