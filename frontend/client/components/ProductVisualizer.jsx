import React from 'react';
import { Modal, OverlayTrigger, Popover, Button, 
    FormGroup, FormControl, ControlLabel, Alert } from 'react-bootstrap';
import { LineChart, Line, CartesianGrid, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';
import { BootstrapTable, TableHeaderColumn } from 'react-bootstrap-table';
import NewAssignmentModal from './NewAssignmentModal.jsx';

export default class ProductVisualizer extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            showNewAssignmentModal: false,
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
        var modalChart;
        if (this.props.productData) {
                modalChart = (<ResponsiveContainer width="100%" height={240}>
                    <LineChart data={this.props.productData.snapshots}>
                        <Line type="monotone" dataKey="list_price" stroke="#8884d8" />
                        <Line type="monotone" dataKey="salesrank" stroke="#8884d8" />
                        <CartesianGrid stroke="#ccc" />
                        <XAxis dataKey="timestamp" />
                        <YAxis />
                        <Tooltip />
                    </LineChart>
                </ResponsiveContainer>)
        }

        var openInNewTab = function(url) {
          var win = window.open(url, '_blank');
          win.focus();
        }

        var selectedTshirtInfo;
        if (this.props.selectedProduct) {
            var tshirt = this.props.selectedProduct;
            var image = tshirt.image || "";
            image = image.replace("._SL75", "._SL200");

            selectedTshirtInfo = (
                <div>
                    <div className="text-center" style={{marginBottom: "20px"}}>
                        <img src={image} style={{height: "200px", "maxWidth": "200px"}} />
                    </div>
                    <p>Title: {tshirt.title}</p>
                    <p>Brand: {tshirt.brand}</p>
                    <p>ASIN: <a href="#a" onClick={openInNewTab.bind(null, "https://www.amazon.com/dp/" + tshirt.asin)}> 
                     {tshirt.asin}
                    </a></p>
                    <p>BSR: {tshirt.salesrank ? tshirt.salesrank : "Not Found"}</p>
                    <p>List Price: {tshirt.list_price ? tshirt.list_price : "Not Found"}</p>
                </div>
            )
            /*
            selectedTshirtInfo = (
                <div>
                    <div className="text-center" style={{marginBottom: "20px"}}>
                        <img src={image} style={{height: "200px", "maxWidth": "200px"}} />
                    </div>
                    <p>Title: {tshirt.title}</p>
                    <p>Brand: {tshirt.brand}</p>
                    <p>ASIN: {tshirt.asin}</p>
                    <p>BSR: {tshirt.salesrank ? tshirt.salesrank : "Not Found"}</p>
                    <p>List Price: {tshirt.list_price ? tshirt.list_price : "Not Found"}</p>
                    <p>eScore: {tshirt.escore ? tshirt.escore : "Not Found"}</p>
                    <p>Weighted eScore V1: {tshirt.weighted_escore_v1 ? tshirt.weighted_escore_v1 : "Not Found"}</p>
                    <p>Weighted eScore V2: {tshirt.weighted_escore_v2 ? tshirt.weighted_escore_v2 : "Not Found"}</p>
                    <p>Streak Score V1: {tshirt.streak_score_v1 ? tshirt.streak_score_v1 : "Not Found"}</p>
                    <p>Streak Score V2: {tshirt.streak_score_v2 ? tshirt.streak_score_v2 : "Not Found"}</p>
                </div>
            )
            */
        } else {
            selectedTshirtInfo = <p>No details available currently.</p>
        }

        var keywordTrackerTable;
        if (this.props.productData && this.props.productData.keywords.length > 0) {
            var keywords = this.props.productData.keywords;
            var cleanedKeywords = [];
            for (var c=0; c<keywords.length; c++) {
                var keyword = keywords[c];
                if (parseInt(keyword.position) <= 50) {
                    cleanedKeywords.push(keyword)
                }
            }

            var index = cleanedKeywords.length/2;
            if (cleanedKeywords.length%2 !== 0) {
                index = index+1;
            }

            var currDate = (new Date()).toISOString().slice(0,10);
            var csvFilename = currDate + "-" + tshirt.asin + "-keywords.csv";
            keywordTrackerTable = (
                <BootstrapTable 
                        data={cleanedKeywords} 
                        exportCSV={true} 
                        csvFileName={csvFilename}
                        striped={true} 
                        bordered={false} 
                        hover={true} 
                        pagination={false}>
                      <TableHeaderColumn dataAlign="center" dataSort={true} dataField="keyword" isKey={true} editable={false}>Keyword</TableHeaderColumn>
                      <TableHeaderColumn dataSort={true} dataAlign="center" dataField="position" editable={false}>Position</TableHeaderColumn>
                </BootstrapTable>
            )
        } else {
            keywordTrackerTable = (
                <p><small>No keywords are currently tracked for the current ASIN.</small></p>
            )
        }

        var trademarksDiv;
        var relevantTrademarkNodes;
        var otherTrademarkNodes;
        if (this.props.productData && this.props.productData.trademarks) {
            var relevantTrademarks = this.props.productData.trademarks.relevant_trademarks || [];
            var otherTrademarks = this.props.productData.trademarks.other_trademarks || [];
            if (relevantTrademarks.length === 0) {
                relevantTrademarkNodes = (
                    <p><small>No trademarks found.</small></p>
                )
            } else {
                relevantTrademarkNodes = relevantTrademarks.map(function(trademark) {
                    const popoverHoverFocus = (
                        <Popover id="popover-trigger-hover-focus" title="TRADEMARKS IN-DEPTH">
                            <p>Description: {trademark.description}</p>
                            <p>Code: {trademark.code}</p>
                            <p>Serial Number: {trademark.serialnumber}</p>

                        </Popover>
                    );

                    return (
                        <OverlayTrigger trigger={['hover', 'focus']} placement="right" overlay={popoverHoverFocus}>
                        <p style={{marginBottom:"0px"}}>
                            <a href="#a">{trademark.wordmark} 
                                <small>
                                    <span style={{fontWeight: 300}}> (Registered {trademark.registrationdate})</span>
                                </small>
                            </a>
                        </p>
                        </OverlayTrigger>
                    )
                })            
            }

            if (otherTrademarks.length === 0) {
                otherTrademarkNodes = (
                    <p><small>No trademarks found.</small></p>
                )
            } else {

                otherTrademarkNodes = otherTrademarks.map(function(trademark) {
                    const popoverHoverFocus = (
                        <Popover id="popover-trigger-hover-focus" title="TRADEMARKS IN-DEPTH">
                            <p>Description: {trademark.description}</p>
                            <p>Code: {trademark.code}</p>
                            <p>Serial Number: {trademark.serialnumber}</p>

                        </Popover>
                    );

                    return (
                        <OverlayTrigger trigger={['hover', 'focus']} placement="right" overlay={popoverHoverFocus}>
                        <p style={{marginBottom:"0px"}}>
                            <a href="#a">{trademark.wordmark} 
                                <small>
                                    <span style={{fontWeight: 300}}> (Registered {trademark.registrationdate})</span>
                                </small>
                            </a>
                        </p>
                        </OverlayTrigger>
                    )
                })
            }      
            trademarksDiv = (
                <div>
                    <p style={{marginBottom:"5px", borderBottom:"1px solid #eee"}}><small>(RELEVANT TO APPAREL)</small></p>
                    {relevantTrademarkNodes}
                    <br />
                    <p style={{marginBottom:"5px", borderBottom:"1px solid #eee"}}><small>(OTHER)</small></p>
                    {otherTrademarkNodes}
                    <br />
                </div>
            )
        } else {
            trademarksDiv = (
                <div>
                    <p><small>We don't have trademarks data currently on this ASIN.</small></p>
                    <button className="btn btn-default btn-sm">
                        RUN TRADEMARK CHECK NOW
                    </button>
                </div>
            )        
        }


        return (
	        <Modal show={this.props.show} onHide={this.props.onHide} bsSize="lg">
	            <Modal.Header closeButton>
	                <h4 className="modal-title" style={{fontWeight:300, fontFamily:'Open Sans'}}>Merch Insider</h4>


	            </Modal.Header>
	            <Modal.Body>
	                <div className="row">
	                    <div className="col-lg-9">

                            <div className="row">
                                <div className="col-lg-12">
                                    <p>PRODUCT HISTORY</p>
                                    <hr style={{marginTop: "0px"}} />
                                </div>
                                <div className="col-lg-1">
                                </div>
                                <div className="col-lg-10">
                                    {modalChart}
                                </div>
                            </div>
                            <br />
                            <div className="row">
                                <div className="col-lg-6" style={{maxHeight: "250px", overflow: "scroll"}}>
                                    <p>KEYWORD TRACKER</p>
                                    <hr style={{marginTop: "0px"}} />
                                    {keywordTrackerTable}
                                </div>

                                <div className="col-lg-6" style={{maxHeight: "250px", overflow: "scroll"}}>
                                    <p>TRADEMARKS TRACKER</p>
                                    <hr style={{marginTop: "0px"}} />
                                    {trademarksDiv}
                                </div>
                            </div>

	                    </div>
	                    <div className="col-lg-3">
	                        <p>PRODUCT DETAILS</p>
	                        <hr style={{marginTop: "0px"}} />
	                        {selectedTshirtInfo}
	                    </div>
	                </div>
	            </Modal.Body>
	        </Modal>
        )
	}

}