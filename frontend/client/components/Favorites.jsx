import React from 'react';
import LoadingIndicator from './LoadingIndicator.jsx'
import ProductVisualizer from './ProductVisualizer.jsx'
import request from 'superagent';

export default class Favorites extends React.Component {
    constructor() {
        super()
        this.state = {
        }
    }

    componentDidMount() {
        var req = request
            .get('/favorites/data/')
            .end(function(err, res) {
                var cache = this.state.cache;
                this.setState({
                    loaded: true,
                    data: JSON.parse(res.text),
                })
            }.bind(this));
    }
    closeModal() {

        console.log("hit here");
        this.setState({
            showModal: false
        })
    }


    toggleAsin(asin) {
        var data = this.state.data;
        var favorites_list = this.state.data.favorites_list;
        var favorites = this.state.data.favorites_by_asin;

        var shouldAdd;
        if (favorites[asin]) {
            console.log("this is favorites", favorites[asin], favorites[asin] === true, favorites[asin] === false)
            // asin was in favorites, but it was already deleted
            if (favorites[asin]["deleted"] && favorites[asin]["deleted"] === true) {
                favorites[asin]["deleted"] = false;
                shouldAdd = true;
            // asin was in favorites but never had deleted key, or deleted key was false. 
            // either way, make sure the asin is deleted.
            } else {
                favorites[asin]["deleted"] = true;
                shouldAdd = false;
            }
        } else {
            // didn't ever find asin before, so we must be toggling it on
            favorites[asin] = {deleted: false}
            shouldAdd = true;
        }
        data.favorites_by_asin = favorites;
        this.setState({
            data: data
        })

        if (shouldAdd) {
            var req = request
                .post('/favorites/add/')
                .send({ asin: asin })
                .end(function(err, res) {
                    // @TODO: Alert user that it worked
                }.bind(this));                
        } else {
            var req = request
                .post('/favorites/delete/')
                .send({ asin: asin })
                .end(function(err, res) {
                    // @TODO: Alert user that it worked
                }.bind(this));                 
        }
    
    }

    showModal(asin) {
        this.setState({
            showModal: true
        })

        var dataByAsin = {};
        this.state.data.favorites_list.map(function(tshirt) {
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

    render() {
        var dataNodes;
        if (this.state.loaded && this.state.data.favorites_list && this.state.data.favorites_list.length > 0) {
            console.log("it was loaded")
            dataNodes = this.state.data.favorites_list.map(function(tshirt) {
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

                var image = tshirt.image;
                image = image.replace("._SL75", "._SL200");

                var openInNewTab = function(url) {
                  var win = window.open(url, '_blank');
                  win.focus();
                }

                var heartStyle = {marginLeft: "5px"}
                if (this.state.loaded && this.state.data && 
                    this.state.data.favorites_by_asin[tshirt.asin] && !this.state.data.favorites_by_asin[tshirt.asin].deleted) {
                    heartStyle["color"] = "red"
                }

                return (
                    <div className="col-lg-3" style={{"height":"270px"}}>
                        <a href="#a" onClick={this.showModal.bind(this, tshirt.asin)}><div className="text-center">
                            <img src={image} style={{height: "130px", "maxWidth": "150px"}} />
                        </div></a>
                        <div className="text-center">
                            <p><label className="label label-primary" style={{fontWeight: 300, paddingBottom: "0px", fontSize: "12px"}}>BSR: {tshirt.salesrank}</label>
                                <a href="#a" onClick={this.toggleAsin.bind(this, tshirt.asin)}>
                                    <i className="fa fa-heart" aria-hidden="true" style={heartStyle}></i>
                                </a>

                                <br/><br />
                                <small>{title} by <b>{brand}</b></small>
                                <br />
                                ASIN: 
                                    <a href="#a" onClick={openInNewTab.bind(null, "https://www.amazon.com/dp/" + tshirt.asin)}>
                                     {tshirt.asin}
                                    </a>
                                <br />
                                Price: <b>${tshirt.list_price}</b>
                            </p>
                        </div>
                    </div>
                )
            }.bind(this))
        } else if (this.state.loaded && this.state.data.favorites_list && this.state.data.favorites_list.length === 0) {
                dataNodes = (
                    <p>You don't have any favorite shirts currently. Go research some to like on the <a href="/home/">Home page</a> and the <a href="/research/">Research page</a>!</p>
                )          
        } else {
                dataNodes = (
                    <LoadingIndicator loadingText="Loading your favorite shirts... " />
                )                 
        }

        return (
            <div>
                <div className="normalheader transition animated fadeIn">
                    <div className="hpanel">
                        <div className="panel-body">
                            <h2 className="font-light m-b-xs" style={{marginTop:"0px", marginBottom:"0px", fontWeight:300, fontFamily: 'Open Sans'}}>
                                Favorites
                            </h2>
                        </div>
                    </div>
                    <br />
                    <div className="hpanel">
                        <div className="panel-body">
                            {dataNodes}
                        </div>
                    </div>
                </div>
                <ProductVisualizer 
                    show={this.state.showModal} productData={this.state.productData} 
                    selectedProduct={this.state.selectedProduct} onHide={this.closeModal.bind(this)}>
                </ProductVisualizer>
            </div>
        );
    }
}
