import React from 'react';
import LoadingIndicator from '../LoadingIndicator.jsx'
import ProductVisualizer from '../ProductVisualizer.jsx'
import request from 'superagent';





export default class WhatsHotThisWeekView extends React.Component {

	constructor(props) {
    	super(props);
        this.state = {
            "showModal": false,
            "productData": null
        }
  	}

    showModal(asin) {
        this.setState({
            showModal: true
        })

        var dataByAsin = {};
        var dataKey = this.props.dataKey;
        this.props.data[dataKey].map(function(tshirt) {
            dataByAsin[tshirt.asin] = tshirt
        })

        var req = request
            .get('/product_metadata/' + asin)
            .end(function(err, res) {
                console.log(res.text)
                this.setState({
                    loaded: true,
                    productData: JSON.parse(res.text),
                    selectedProduct: dataByAsin[asin]
                })
            }.bind(this));

    }

    closeModal() {

        console.log("hit here");
        this.setState({
            showModal: false
        })
    }


	render() {

        var dataNodes;
        var dataKey = this.props.dataKey;
        if (this.props.loaded && this.props.data && this.props.data[dataKey] && this.props.data[dataKey].length > 0) {
            console.log("it was loaded")
             dataNodes = this.props.data[dataKey].map(function(tshirt) {
                var title = tshirt.title;
                var brand = tshirt.brand;
                if (title.length > 30) {
                    title = title.slice(0,30) + "..."
                }
                if (brand.length > 20) {
                    brand = brand.slice(0,30) + "..."
                }

                var last_7d_salesrank = tshirt.last_7d_salesrank;
                var salesrank = tshirt.salesrank;
                var multiplier = (last_7d_salesrank/salesrank).toFixed(1);
                var dropTag = multiplier + "X DROP";


                var image = tshirt.image;
                image = image.replace("._SL75", "._SL200");

                var openInNewTab = function(url) {
                  var win = window.open(url, '_blank');
                  win.focus();
                }

                var heartStyle = {marginLeft: "5px"}
                if (this.props.loaded && this.props.data && 
                    this.props.data.favorites_by_asin[tshirt.asin] && !this.props.data.favorites_by_asin[tshirt.asin].deleted) {
                    heartStyle["color"] = "red"
                }

                return (
                    <div className="col-lg-3" style={{"height":"270px"}}>
                        <a href="#a" onClick={this.showModal.bind(this, tshirt.asin)}><div className="text-center">
                            <img src={image} style={{height: "130px", "maxWidth": "150px"}} />
                        </div></a>
                        <div className="text-center">
                            <p><label className="label label-primary" style={{fontWeight: 300, paddingBottom: "0px", fontSize: "12px"}}>BSR: {tshirt.salesrank} ({dropTag})</label>
                                <a href="#a" onClick={this.props.toggleAsin.bind(null, tshirt.asin)}>
                                    <i className="fa fa-heart" aria-hidden="true" style={heartStyle}></i>
                                </a>

                                <br/><br />
                                <small>{title} by <b>{brand}</b></small>
                                <br />
                                ASIN: <a href="#a" onClick={openInNewTab.bind(null, "https://www.amazon.com/dp/" + tshirt.asin)}> {tshirt.asin}</a>
                                <br />
                                Price: <b>${tshirt.list_price}</b>
                            </p>
                        </div>
                    </div>
                )
            }.bind(this))
        } else if (this.props.loaded && this.props.data && this.props.data[dataKey] && this.props.data[dataKey].length === 0) {
            if (this.props.data.best_sellers && this.props.data.best_sellers.length > 0) {
                dataNodes = (
                    <p>We didn't find any trending t-shirts that dropped in salesrank recently with that query, but <a href="#a" onClick={this.props.showBestSellers}>click here to find {this.props.data.best_sellers.length} tshirts in the 
                         Best Seller Dashboard</a>!
                    </p>
                )
            } else {
                dataNodes = (
                    <p>No data was found in this current dashboard.
                    </p>
                )                
            }
        } else {
            dataNodes = (
                <LoadingIndicator loadingText="Loading merch data... " />
            )
        }

		return (
            <div className="hpanel">
                <div className="panel-body float-e-margins">
                    <h3 style={{fontWeight:"300", fontFamily: "Open Sans", marginTop:"0px"}}>What's Hot</h3>
                    <hr />
                    {dataNodes}
                </div>
                <ProductVisualizer 
                    show={this.state.showModal} productData={this.state.productData} 
                    selectedProduct={this.state.selectedProduct} onHide={this.closeModal.bind(this)}>
                </ProductVisualizer>
            </div>
		  )
		}
	}