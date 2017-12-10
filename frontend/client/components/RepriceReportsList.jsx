import React from 'react';
import LoadingIndicator from './LoadingIndicator.jsx'

export default class TemplateViewer extends React.Component {
	constructor(props) {
    	super(props);
	  	this.state = {loaded: false, reports: []}
  	}

	componentDidMount() {
		this.serverRequest = $.get('/query_reprice_reports', function (result) {
			var repriceReports = JSON.parse(result);
			this.setState({
				reports: repriceReports,
				loaded: true
			});
		}.bind(this));
	}

	render() {
		var table = (
			<BootstrapTable data={this.state.reports} multiColumnSearch={true} striped={true} bordered={false} hover={true}>
				  <TableHeaderColumn isKey={true} dataAlign="center" dataField="template_name" editable={false}>Template Name</TableHeaderColumn>
				  <TableHeaderColumn dataAlign="center" dataField="last_updated" editable={false}>Reprice Timestamp</TableHeaderColumn>
			</BootstrapTable>
		)

		if (!this.state.loaded) {
			table = <LoadingIndicator loadingText="Loading Reports... " />
		}

		return (
            <div className="hpanel">
                <div className="panel-heading hbuilt" style={ {"padding": "10px"} }>
                    <span className="left-pad">Reprice Reports</span>
                    <hr />
                    {table}
                </div>
            </div>
		)
	}

}