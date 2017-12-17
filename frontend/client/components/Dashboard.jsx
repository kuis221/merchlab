import React from 'react';
import BestSellersView from './dashboard/BestSellersView.jsx'
import WhatsHotThisWeekView from './dashboard/WhatsHotThisWeekView.jsx'
import KeywordViewer from './dashboard/KeywordViewer.jsx'
import request from 'superagent';

export default class Dashboard extends React.Component {
    constructor() {
        super()
        this.state = {
            loaded: false,
            data: null,
            query: "",
            dashboardView: "whats_hot_24_hrs",
            cache: {}
        }
    }

    componentDidMount() {

        $("#search").keyup(function (e) {
            if (e.keyCode == 13) {
                setTimeout(function() {
                    if ($("#search").attr("disabled") == undefined) {
                        ////console.log("noticed an enter key too")
                        this.search();                              
                    }
                }.bind(this), 100)
            }
        }.bind(this));

        var req = request
            .get('/dashboard_data/')
            .end(function(err, res) {
                var cache = this.state.cache;
                cache[""] = JSON.parse(res.text);
                this.setState({
                    loaded: true,
                    data: JSON.parse(res.text),
                    cache: cache
                })
            }.bind(this));
    }

    showBestSellers() {
        this.setState({
            dashboardView: "best_sellers"
        })
    }

    setDashboard(dashboardView) {
        this.setState({
            dashboardView: dashboardView
        })
    }

    formatDashboardView(dashboardView) {
        if (dashboardView === "whats_hot_24_hrs") {
            return "What's Hot - Last 24 Hours";
        } else if (dashboardView === "whats_hot_last_7d") { 
            return "What's Hot - Last 7 Days";
        } else if (dashboardView === "best_sellers") {
            return "Best Sellers";
        } else if (dashboardView === "whats_hot_escore") {
            return "What's Hot - eScore"
        } else if (dashboardView === "whats_hot_weighted_escore_v1") {
            return "What's Hot - Weighted eScore V1"

        } else if (dashboardView === "whats_hot_weighted_escore_v2") {
            return "What's Hot - Weighted eScore V2"

        } else if (dashboardView === "whats_hot_streak_score_v1") {
            return "What's Hot - Streak Score V1"

        } else if (dashboardView === "whats_hot_streak_score_v2") {
            return "What's Hot - Streak Score V2"
        } else if (dashboardView === "consistent_winners") {
            return "Consistent Winners"
        } else if (dashboardView === "recently_discovered_shirts") {
            return "Recently Discovered Shirts"
        }
    }

    searchWithQuery(query) {
        console.log("this is this", this)
        console.log("this is query", query);
        this.setState({
            loaded: false,
            data: null
        })

        $("#search").val(query);
        var req = request
            .post('/dashboard/search/')
            .send({ query: query })
            .end(function(err, res) {
                this.setState({
                    loaded: true,
                    data: JSON.parse(res.text)
                })
            }.bind(this));          
    }

    search() {
        var query = $("#search").val();

        if (this.state.cache[query]) {
            this.setState({
                data: this.state.cache[query]
            })
            return
        }

        this.setState({
            loaded: false,
            data: null
        })

        console.log(query);
        var req = request
            .post('/dashboard/search/')
            .send({ query: query })
            .end(function(err, res) {
                var cache = this.state.cache;
                cache[query] = JSON.parse(res.text)
                this.setState({
                    loaded: true,
                    data: JSON.parse(res.text),
                    cache: cache
                })
            }.bind(this));        
    }

    toggleAsin(asin) {
        var data = this.state.data;
        var favorites = data.favorites_by_asin;

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

    render() {

        var dashboardView = this.state.dashboardView;
        var formattedDashboardView = this.formatDashboardView(dashboardView);
        var dashboardToDisplay;
        if (this.state.dashboardView === "whats_hot_24_hrs") {
            dashboardToDisplay = (
                <WhatsHotThisWeekView loaded={this.state.loaded} data={this.state.data} dataKey="whats_hot_this_week" toggleAsin={this.toggleAsin.bind(this)} showBestSellers={this.showBestSellers.bind(this)}/>
            ) 
        } else if (this.state.dashboardView === "whats_hot_last_7d") {
            dashboardToDisplay = (
                <WhatsHotThisWeekView loaded={this.state.loaded} data={this.state.data} dataKey="whats_hot_last_7d" toggleAsin={this.toggleAsin.bind(this)} showBestSellers={this.showBestSellers.bind(this)}/>
            ) 
        } else if (this.state.dashboardView === "best_sellers") {
            dashboardToDisplay = (
                <BestSellersView loaded={this.state.loaded} data={this.state.data} />
            )
        } else if (this.state.dashboardView === "whats_hot_escore") {
            dashboardToDisplay = (
                <WhatsHotThisWeekView 
                    loaded={this.state.loaded} 
                    data={this.state.data} 
                    dataKey="whats_hot_escore"
                    showBestSellers={this.showBestSellers.bind(this)}
                />
            )             
        } else if (this.state.dashboardView === "whats_hot_weighted_escore_v1") {
            dashboardToDisplay = (
                <WhatsHotThisWeekView 
                    loaded={this.state.loaded} 
                    data={this.state.data} 
                    dataKey="whats_hot_weighted_escore_v1"
                    showBestSellers={this.showBestSellers.bind(this)}
                />
            )                         
        } else if (this.state.dashboardView === "whats_hot_weighted_escore_v2") {
            dashboardToDisplay = (
                <WhatsHotThisWeekView 
                    loaded={this.state.loaded} 
                    data={this.state.data} 
                    dataKey="whats_hot_weighted_escore_v2"
                    showBestSellers={this.showBestSellers.bind(this)}
                />
            )                         
        } else if (this.state.dashboardView === "whats_hot_streak_score_v1") {
            dashboardToDisplay = (
                <WhatsHotThisWeekView 
                    loaded={this.state.loaded} 
                    data={this.state.data} 
                    dataKey="whats_hot_streak_score_v1"
                    showBestSellers={this.showBestSellers.bind(this)}
                />
            )                         
        } else if (this.state.dashboardView === "whats_hot_streak_score_v2") {
            dashboardToDisplay = (
                <WhatsHotThisWeekView 
                    loaded={this.state.loaded} 
                    data={this.state.data} 
                    dataKey="whats_hot_streak_score_v2"
                    showBestSellers={this.showBestSellers.bind(this)}
                />
            )                         
        } else if (this.state.dashboardView === "consistent_winners") {
            dashboardToDisplay = (
                <WhatsHotThisWeekView 
                    loaded={this.state.loaded} 
                    data={this.state.data} 
                    dataKey="whats_hot_streak_score_v2"
                    toggleAsin={this.toggleAsin.bind(this)}
                    showBestSellers={this.showBestSellers.bind(this)}
                />
            )                  
        } else if (this.state.dashboardView === "recently_discovered_shirts") {
            dashboardToDisplay = (
                <WhatsHotThisWeekView 
                    loaded={this.state.loaded} 
                    data={this.state.data} 
                    dataKey="recently_discovered_shirts"
                    toggleAsin={this.toggleAsin.bind(this)}
                    showBestSellers={this.showBestSellers.bind(this)}
                />
            )          
        }

        return (
            <div>
                <div className="normalheader transition animated fadeIn">
                    <div className="hpanel">
                        <div className="panel-body">
                            <h2 className="font-light m-b-xs" style={{marginTop:"0px", marginBottom:"0px", fontWeight:300, fontFamily: 'Open Sans'}}>
                                The Feed
                            </h2>
                        </div>
                    </div>
                </div>

                <div className="content animate-panel">
                    <div className="row">
                        <div className="col-lg-12">
                            <div  className="hpanel">
                                <div className="hpanel-body">
                                    <div className="input-group margin-bottom">
                                        <div className="input-group-btn">

                                            <button className="btn btn-default dropdown-toggle" data-toggle="dropdown" type="button">
                                            <span className="margin-right">Current Feed: <span id="current-feed">{formattedDashboardView}</span></span> 
                                            <span className="caret"></span></button>
                                            <ul className="dropdown-menu dropdown-menu-left">
                                                <li><a href="#a" onClick={this.setDashboard.bind(this, "whats_hot_24_hrs")}>What's Hot - Last 24 Hrs</a></li>
                                                <li><a href="#a" onClick={this.setDashboard.bind(this, "whats_hot_last_7d")}>What's Hot - Last 7 Days</a></li>
                                                <li><a href="#a" onClick={this.setDashboard.bind(this, "consistent_winners")}>Consistent Winners</a></li>
                                            </ul>
                                        </div>
                                        <input type="text" id="search" className="form-control" placeholder="Search a keyword..."/>
                
                                        <span className="input-group-btn">
                                            <button onClick={this.search.bind(this)} tabIndex="-1" className="btn btn-default" type="button">
                                                <i className="pe-7s-search margin-right"></i></button>
                                        </span>
                                    </div>
                                </div>
                            </div>
                            {dashboardToDisplay}

                        </div>
                    </div>
                </div>
            </div>
        );
    }
}
