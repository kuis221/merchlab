import React from 'react';
import LoadingIndicator from '../LoadingIndicator.jsx'
import request from 'superagent';

export default class KeywordViewer extends React.Component {

	constructor(props) {
    	super(props);
        this.state = {
        }
  	}

	render() {

        var caption = this.props.caption || "";
        var captionTag;
        if (caption != "") {
            captionTag = (<div><small>{caption}</small><br /><br /></div>)
        }
        var title = this.props.title || "Trending Title Keywords";

        var bodyContent;
        if (this.props.keywords){
            var keywords = this.props.keywords;
            var keywordNodes;
            if (keywords.length === 0) {
                keywordNodes = <p>No keywords found unfortunately.</p>
                captionTag = undefined;
            } else {
                keywordNodes = keywords.map(function(keyword) {
                    return (
                        <p>
                            <a href="#a" onClick={this.props.search.bind(null, keyword.id)}>{keyword.id} </a> 
                            <small>({keyword.count} shirts found)</small>
                        </p>
                    )

                }.bind(this))                
            }

            var bodyContent = (
                <div className="panel-body float-e-margins">
                    <h4 style={{marginTop:"0px", fontSize: "16px"}}>{title}</h4>
                    <hr style={{marginTop: "0px"}} />
                    {captionTag}
                    {keywordNodes}
                </div>
            )            
        } else {
            var bodyContent = (
                <div className="panel-body float-e-margins">
                    <LoadingIndicator 
                        loadingText="Loading common phrases... "
                    />
                </div>
            )              
        }


		return (
            <div className="hpanel" style={{maxHeight:"850px", overflow: "scroll"}} >
                {bodyContent}
            </div>
		  )
		}
	}