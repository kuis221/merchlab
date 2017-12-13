import React from 'react';
import LoadingIndicator from './LoadingIndicator.jsx'
import { BootstrapTable, TableHeaderColumn } from 'react-bootstrap-table';
import ProductVisualizer from './ProductVisualizer.jsx'
import request from 'superagent';
import KeywordViewer from './dashboard/KeywordViewer.jsx'

export default class InventoryTable extends React.Component {

	constructor(props) {
    	super(props);
	  this.state = {
		items: [],
		loaded: false,
        "showModal": false,
        "productData": null,
        "recentSearchesLoaded": false,
        "recentSearches": null
	  }
  	}

	componentDidMount() {
        $("#keyword-search").keyup(function (e) {
            if (e.keyCode == 13) {
                setTimeout(function() {
                    if ($("#keyword-search").attr("disabled") == undefined) {
                        ////console.log("noticed an enter key too")
                        this.search();                              
                    }
                }.bind(this), 100)
            }
        }.bind(this));

		this.serverRequest = $.get('/recent_searches/merch_researcher/', function (result) {
			var response = JSON.parse(result);
			this.setState({
				recentSearches: response,
				recentSearchesLoaded: true
			});
		}.bind(this));	

		this.searchWithQuery("");

	}

	imgFormatter(cell, row) {

		return (
	    	<a href="#a" onClick={this.showModal.bind(this, row)}>
	    		<img style={{height: "100px"}} src={row.image}></img>
	    	</a>
	  	)
	}

	productDetailsFormatter(cell, row) {
        var heartStyle = {marginLeft: "5px"}
        if (this.state.loaded && this.state.favoritesByAsin && 
            this.state.favoritesByAsin[row.asin] && !this.state.favoritesByAsin[row.asin].deleted) {
            heartStyle["color"] = "red"
        }

		return (
			<p>
				List Price: ${row.list_price}
				<br />
				Salesrank: {row.salesrank || "THROTTLED"}
				<br /><br />
	            <a href="#a" onClick={this.toggleAsin.bind(this, row.asin)}>
	                <i className="fa fa-heart" aria-hidden="true" style={heartStyle}></i>
	            </a>
			</p>
		)
	}

	titleFormatter(cell, row) {
        var openInNewTab = function(url) {
          var win = window.open(url, '_blank');
          win.focus();
        }

		return (
			<p>{row.title} by <b>{row.brand}</b>
			<br />
			<small>ASIN: 
				<a href="#a" onClick={openInNewTab.bind(null, "https://www.amazon.com/dp/" + row.asin)}>
            	{row.asin}</a>
            </small>
			</p>
		)
	}

    showModal(product) {
        this.setState({
            showModal: true
        })

        var req = request
            .get('/product_metadata/' + product.asin)
            .end(function(err, res) {
                console.log(res.text)
                this.setState({
                    loaded: true,
                    productData: JSON.parse(res.text),
                    selectedProduct: product
                })
            }.bind(this));

    }

    closeModal() {

        console.log("hit here");
        this.setState({
            showModal: false
        })
    }

    searchWithQuery(query) {
    	$("#keyword-search").val(query);
    	var recentSearches = this.state.recentSearches || [];
    	recentSearches.unshift(query);
		

		this.setState({
			loaded: false,
			recentSearches: recentSearches
		})
		var data = {
			query: query
		}

		this.serverRequest = $.post('/keyword_search/', data, function (result) {
			var response = JSON.parse(result);
			this.setState({
				items: response.results,
				keywords: response.keywords,
				favoritesByAsin: response.favorites_by_asin,
				loaded: true
			});
		}.bind(this));		    	
    }

	search() {
		var query = $("#keyword-search").val();
		this.searchWithQuery(query)
	}

    toggleAsin(asin) {
        var favorites = this.state.favoritesByAsin;

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
            console.log("never found it before, gonna toggle it on")
            favorites[asin] = {deleted: false}
            shouldAdd = true;
        }
        this.setState({
            favoritesByAsin: favorites
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

	render() {
	  	var table;
	  	console.log("abc")
	  	console.log(this)
	  	console.log(this.state)
	  	if (!this.state.loaded) {
			table = (
		  		<LoadingIndicator loadingText="Loading merch data... " />
			)
	  	} else {

			function onRowSelect(row, isSelected){
			  console.log(row);
			  console.log("selected: " + isSelected)
			}

			function onSelectAll(isSelected){
			  console.log("is select all: " + isSelected);
			}
			var selectRowProp = {
			  mode: "checkbox",
			  clickToSelect: true,
			  bgColor: "rgb(238, 193, 213)",
			  onSelect: onRowSelect,
			  onSelectAll: onSelectAll
			};


			var options = {
			  		sizePerPage: 50,
			  		sizePerPageList: [10, 50, 100],
			  		paginationSize: 10
			}

			var cellEditProp = {
			  mode: "click",
			  blurToSave: true,
			};

			table = (
			  	<BootstrapTable 
			  		data={this.state.items} 
			  		exportCSV={false} 
			  		striped={false} 
			  		bordered={false} 
			  		hover={true} 
			  		pagination={true} 
			  		cellEdit={cellEditProp}
			  		options={options}>
				  <TableHeaderColumn dataAlign="center" dataSort={true} dataField="image" editable={false} dataFormat={this.imgFormatter.bind(this)}>Image</TableHeaderColumn>
				  <TableHeaderColumn dataSort={true} dataAlign="center" dataField="asin" isKey={true} editable={false} dataFormat={this.titleFormatter}>Title</TableHeaderColumn>
				  <TableHeaderColumn dataAlign="center" dataSort={true} dataField="salesrank" editable={false} dataFormat={this.productDetailsFormatter.bind(this)}>Product Details</TableHeaderColumn>
			  	</BootstrapTable>
			)
		}

        var keywords;
        if (this.state.loaded && this.state.keywords) {
            keywords = this.state.keywords;
        }

        var keywordViewer = (
            <KeywordViewer 
                keywords={keywords}
                title="Common Phrases"
                caption="These are the most commonly used phrases from the results we discovered!"
                search={this.searchWithQuery.bind(this)}>
            </KeywordViewer>
        )


        var recentSearches;

        if (this.state.recentSearchesLoaded) {
	        recentSearches = this.state.recentSearches.map(function(search) {
	            return (
	                <p>
	                    <a href="#a" onClick={this.searchWithQuery.bind(this, search.query)}>{search.query} </a> 
	                </p>
	            )

	        }.bind(this))    
        } else {
        	recentSearches = <LoadingIndicator loadingText="Loading recent searches... " />
        }

		return (

			<div>
                <ProductVisualizer 
                    show={this.state.showModal} productData={this.state.productData} 
                    selectedProduct={this.state.selectedProduct} onHide={this.closeModal.bind(this)}>
                </ProductVisualizer>
				<div className="row">
				   	<div className="col-lg-12">
						<div className="hpanel">
							<div className="panel-body">
								<h3 className="font-light m-b-xs">
								  <span className="margin-right" style={{marginLeft: "10px", fontWeight: 300, fontFamily: "Open Sans"}}>Merch Researcher [BETA]</span>
								</h3>
								<div className="input-group" style={{padding: "10px"}}>
	                                <input className="form-control" type="text" placeholder="Search keywords.." id="keyword-search" />
	                                <div className="input-group-btn">
	                                    <button className="btn btn-default" onClick={this.search.bind(this)}><i className="fa fa-search"></i></button>
	                                </div>
	                            </div>
							</div>
						</div>
					</div>
				</div>
				<div className="row">
				   	<div className="col-lg-9">
						<div className="hpanel">
							<div className="panel-body">
								{table}
							</div>
						</div>
					</div>

                    <div className="col-lg-3">
						<div className="hpanel" style={{maxHeight:"350px", overflow: "scroll"}}>
							<div className="panel-body">
								<h4 style={{marginTop:"0px", fontSize: "16px"}}>Recent Searches</h4>
                    			<hr style={{marginTop: "0px"}} />
                    			{recentSearches}
							</div>
						</div>
                        {keywordViewer}
                    </div>
				</div>
			</div>
		  )
		}
	}