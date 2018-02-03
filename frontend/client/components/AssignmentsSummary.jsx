import React from 'react';

export default class AssignmentSummary extends React.Component {
    render() {
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
    }
}