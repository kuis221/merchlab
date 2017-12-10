import React from 'react';
import LoadingIndicator from '../LoadingIndicator.jsx'
import ProductVisualizer from '../ProductVisualizer.jsx'
import request from 'superagent';

export default class BestSellersView extends React.Component {

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
        this.props.data.best_sellers.map(function(tshirt) {
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
        this.setState({
            showModal: false
        })
    }

	render() {
        var dataNodes;
        if (this.props.loaded && this.props.data && this.props.data.best_sellers && this.props.data.best_sellers.length > 0) {
            console.log("it was loaded and we have data")
            dataNodes = this.props.data.best_sellers.map(function(tshirt) {
                var title = tshirt.title;
                var brand = tshirt.brand;
                if (title.length > 30) {
                    title = title.slice(0,30) + "..."
                }
                if (brand.length > 20) {
                    brand = brand.slice(0,30) + "..."
                }

                var image = tshirt.image;
                image = image.replace("._SL75", "._SL200");

                return (
                    <a href="#a" onClick={this.showModal.bind(this, tshirt.asin)}><div className="col-lg-3" style={{"height":"250px"}}>
                        <div className="text-center">
                            <img src={image} style={{height: "130px", "maxWidth": "150px"}} />
                        </div>
                        <div className="text-center">
                            <p>BSR: <b>{tshirt.salesrank}</b> | 
                                Price: <b>${tshirt.list_price}</b><br/>
                                <small>{title} by <b>{brand}</b></small>
                                <br />
                                ASIN: {tshirt.asin}
                            </p>
                        </div>
                    </div></a>
                )
            }.bind(this))
        } else if (this.props.loaded && this.props.data && this.props.data.best_sellers && this.props.data.best_sellers.length === 0) {
            var dataNodes = (
                <p>Sorry, no data was found in this dashboard.</p>
            )
        }

		return (
            <div className="hpanel">
                <div className="panel-body float-e-margins">
                    <h3 style={{fontWeight:"300", fontFamily: "Open Sans", marginTop:"0px"}}>Best Sellers</h3>
                    <p>These are the top selling Merch By Amazon shirts, updated daily.</p>
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