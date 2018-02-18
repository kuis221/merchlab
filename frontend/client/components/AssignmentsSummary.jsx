import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Select from 'react-select';

export default class AssignmentSummary extends React.Component {
    
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
        /*
        return (
            <div className="row">
                <div className="col-lg-4">
                    <div className="hpanel">
                        <div className="panel-body text-center" style={{height:'230px'}}>
                            <div className="stats-title pull-left">
                                <h4>Summary</h4>
                            </div>
                            <br /><br /><br />
                            <i className="pe-7s-graph2 fa-4x"></i>
                            <h2 className="m-xs" style={{fontWeight:300, fontFamily:'Open Sans'}}>482 DESIGNS MADE</h2>
                            <p><strong>(8.0% <i className="fa fa-level-up text-success"></i> from last week)</strong></p>
                        </div>
                    </div>
                </div>
                <div className="col-lg-4">
                    <div className="hpanel stats">
                        <div className="panel-body list" style={{height: '230px'}}>
                            <div className="stats-title pull-left">
                                <h4>Designer Breakdown</h4>
                            </div>



                            <div className="stats-icon pull-right">
                                <i className="pe-7s-display1 fa-4x"></i>
                            </div>
                            <div className="m-t-xl">
                                <small>
                                    Breakdown of uploads from your most active designers.
                                </small>
                            </div>


                            <div className="progress m-t-xs full">
                                <div style={{width: '95%'}}  aria-valuemax="100" aria-valuemin="0" aria-valuenow="95" role="progressbar" className=" progress-bar progress-bar-success">
                                    <span style={{fontWeight: 300, fontSize: '10px'}}>Mark (80%)</span>
                                </div>
                            </div>

                            <div className="progress m-t-xs full">
                                <div style={{width: '55%'}}  aria-valuemax="100" aria-valuemin="0" aria-valuenow="55" role="progressbar" className=" progress-bar progress-bar-success">
                                    <span style={{fontWeight: 300, fontSize: '10px'}}>Joe (14%)</span>
                                </div>
                            </div>

                            <div className="progress m-t-xs full">
                                <div style={{width: '35%'}}  aria-valuemax="100" aria-valuemin="0" aria-valuenow="35" role="progressbar" className=" progress-bar progress-bar-success">
                                    <span style={{fontWeight: 300, fontSize: '10px'}}>Bob (10%)</span>
                                </div>
                            </div>
                            <div className="progress m-t-xs full">
                                <div style={{width: '20%'}} aria-valuemax="100" aria-valuemin="0" aria-valuenow="25" role="progressbar" className=" progress-bar progress-bar-success">
                                    <span style={{fontWeight: 300, fontSize: '10px'}}>Tim (8%)</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="col-lg-4">
                    <div className="hpanel stats">
                        <div className="panel-body" style={{height: '230px'}}>
                            <div className="stats-title pull-left">
                                <h4>Assignment Statuses</h4>
                            </div>
                            <div className="stats-icon pull-right">
                                <i className="pe-7s-battery fa-4x"></i>
                            </div>
                            <div className="clearfix"></div>
                            <div className="m-t-xs">

                                <div className="row">
                                    <div className="col-xs-6">
                                        <small className="stat-label">Unassigned</small>
                                        <h4>8</h4>
                                    </div>
                                    <div className="col-xs-6">
                                        <small className="stat-label">Assigned</small>
                                        <h4>65</h4>
                                    </div>
                                </div>
                                <div className="row">
                                    <div className="col-xs-6">
                                        <small className="stat-label">Completed</small>
                                        <h4>43</h4>
                                    </div>
                                    <div className="col-xs-6">
                                        <small className="stat-label">Deleted</small>
                                        <h4>2</h4>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        )
        */

        var designers = this.props.designers || [];
        console.log(designers);

        var designerAssignmentsData = [];
        for (var c=0; c<designers.length; c++) {
            var designer = designers[c];
            var currData = {
                designer_username: designer.designer_username,
                "Assigned": (designer.status_breakdown || {}).assigned || 0,
                "Completed": (designer.status_breakdown || {}).completed || 0                
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

        var chart = (<ResponsiveContainer width="100%" height={243}>
            <BarChart data={designerAssignmentsData}
                margin={{top: 5, right: 30, left: 20, bottom: 5}}>
                <XAxis dataKey="designer_username"/>
                <YAxis/>
                <CartesianGrid strokeDasharray="3 3"/>
                <Tooltip/>
                <Legend />
                <Bar dataKey="Assigned" fill="#8884d8" />
                <Bar dataKey="Completed" fill="#82ca9d" />
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
                        <div className="panel-body list">
                            {analyticsRangeSelect}
                            <div className="list-item-container">
                                <div className="list-item">
                                    <h3 className="no-margins font-extra-bold">34</h3>
                                    <small>Completed Assignments</small>
                                    <div className="pull-right font-bold">98% <i className="fa fa-level-up text-success"></i></div>
                                </div>
                                <div className="list-item">
                                    <h3 className="no-margins font-extra-bold">2,773</h3>
                                    <small>Total Uploads</small>
                                    <div className="pull-right font-bold">98% <i className="fa fa-level-up text-success"></i></div>
                                </div>
                                <div className="list-item">
                                    <h3 className="no-margins font-extra-bold text-success">4,422</h3>
                                    <small>Approved Uploads</small>
                                    <div className="pull-right font-bold">13% <i className="fa fa-level-down text-color3"></i></div>
                                </div>
                                <div className="list-item">
                                    <h3 className="no-margins font-extra-bold text-danger">9,180</h3>
                                    <small>Rejected Uploads</small>
                                    <div className="pull-right font-bold">22% <i className="fa fa-bolt text-color3"></i></div>
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
                                <div className="col-lg-3" style={{float: 'right', marginRight: '28.5px', marginBottom:'20px'}}>
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