import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Select from 'react-select';

export default class DesignersSummary extends React.Component {
    
    constructor(props) {
        super(props);
        this.state = {
            uploadAnalyticsDateRange: "This Week",
            designerBreakdownDateRange: "This Week"
        }
    }

    handleChangeUploadAnalyticsDateRange(selectedOption) {
        this.setState({
            uploadAnalyticsDateRange: selectedOption
        })
    }

    handleChangeDesignerBreakdownDateRange(selectedOption) {
        this.setState({
            designerBreakdownDateRange: selectedOption
        })
    }

    render() {

        var designers = this.props.designers || [];
        console.log(designers);

        var designerAssignmentsData = [];
        for (var c=0; c<designers.length; c++) {
            var designer = designers[c];
            var currData = {
                designer_username: designer.designer_username,
                "Approved Pending Payout": designer.approved_commission_amount,
                "Pending Amount": designer.unapproved_commission_amount    
            }
            designerAssignmentsData.push(currData);
        }
        console.log("this is state", )
        var analyticsRangeSelect = (<Select
            name="upload-analytics-date-range"
            value={this.state.uploadAnalyticsDateRange}
            onChange={this.handleChangeUploadAnalyticsDateRange.bind(this)}
            searchable={false}
            options={[
                { value: 'This Week', label: 'This Week' },
                { value: 'Last Week', label: 'Last Week' },
                { value: 'This Month', label: 'This Month' },
            ]}
        />)

        var designerBreakdownRangeSelect = (<Select
            name="upload-analytics-date-range"
            value={this.state.designerBreakdownDateRange}
            onChange={this.handleChangeUploadAnalyticsDateRange.bind(this)}
            searchable={false}
            options={[
                { value: 'This Week', label: 'This Week' },
                { value: 'Last Week', label: 'Last Week' },
                { value: 'This Month', label: 'This Month' },
            ]}
        />)

        var chart = (<ResponsiveContainer width="100%" height={168}>
            <BarChart data={designerAssignmentsData}
                margin={{top: 5, right: 30, left: 20, bottom: 5}}>
                <XAxis dataKey="designer_username"/>
                <YAxis/>
                <CartesianGrid strokeDasharray="3 3"/>
                <Tooltip/>
                <Legend />
                <Bar dataKey="Approved Pending Payout" fill="#8884d8" />
                <Bar dataKey="Pending Amount" fill="#82ca9d" />
            </BarChart>
        </ResponsiveContainer>)

        return (
            <div className="row">
                <div className="col-lg-4">
                    <div className="hpanel">
                        <div className="panel-heading hbuilt">
                            <div className="panel-tools">
                                <a className="showhide">
                                    <i className="fa fa-chevron-up"></i>
                                </a>
                            </div>
                            <span style={{marginLeft: '10px'}}>Upload Analytics</span>
                        </div>
                        <div className="panel-body">
                            <div style={{marginBottom: '10px'}}>{analyticsRangeSelect}</div>
                            <div className="stats-title pull-left">
                                <h4>Total Team Payout</h4>
                            </div>
                            <div className="stats-icon pull-right">
                                <i className="pe-7s-cash fa-4x"></i>
                            </div>
                            <div className="clearfix"></div>
                            <div className="m-t-xs">

                                <div className="row">
                                    <br />
                                    <div className="col-xs-12" style={{marginBottom:'15px'}}>
                                        <small>This is how much your designers are owed at the next payout period.</small>
                                    </div>

                                    <div className="col-xs-5">
                                        <small className="stat-label">Last Week</small>
                                        <h4>$230.00 </h4>
                                    </div>
                                    <div className="col-xs-7">
                                        <small className="stat-label">This week</small>
                                        <h4>$798060.00 <i className="fa fa-level-up text-success"></i></h4>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="col-lg-8">
                    <div className="hpanel">
                        <div className="panel-heading hbuilt">
                            <div className="panel-tools">
                                <a className="showhide">
                                    <i className="fa fa-chevron-up"></i>
                                </a>
                            </div>
                            <span style={{marginLeft: '10px'}}>Breakdown By Designer</span>
                        </div>
                        <div className="panel-body text-center">
                            <div className="row">
                                <div className="col-lg-3" style={{float: 'right', marginRight: '28.5px', marginBottom:'10px'}}>
                                    {designerBreakdownRangeSelect}
                                </div>
                            </div>
                            {chart}
                        </div>
                    </div>
                </div>
            </div>
        )

    }
}