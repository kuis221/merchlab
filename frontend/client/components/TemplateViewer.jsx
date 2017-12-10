import React from 'react';
import LoadingIndicator from './LoadingIndicator.jsx'
import { BootstrapTable, TableHeaderColumn } from 'react-bootstrap-table';
import { Modal, OverlayTrigger, Popover, Tooltip, Button, 
	FormGroup, FormControl, ControlLabel } from 'react-bootstrap';

export default class TemplateViewer extends React.Component {
	constructor(props) {
    	super(props);
	  	this.state = {loaded: false, templates: [], showCreateTemplateModal: false, templateName: "", newTemplateAdded: false}
  	}

	componentDidMount() {
		this.serverRequest = $.get('/query_templates', function (result) {
			var templates = JSON.parse(result);
			this.setState({
				templates: templates,
				loaded: true
			});
		}.bind(this));
	}

	showCreateTemplateModal() {
		this.setState({
			showCreateTemplateModal: true
		})
	}

	closeCreateTemplateModal() {
		this.setState({
			showCreateTemplateModal: false
		})
	}

	validateTemplateName() {
		var templates = this.state.templates;
		for (var c=0; c<templates.length; c++) {
			if (this.state.templateName === templates[c].name) {
				return 'error'
			}
		}
		return 'success'
	}

	handleTemplateNameChange(e) {
	    this.setState({ templateName: e.target.value });
	}

	createTemplate() {
		if (this.validateTemplateName()) {
			var data = {
				name: this.state.templateName
			}

			$.ajax({
			  	type: "POST",
			  	url: "/add_template",
			  	data: data,
			  	success: function() {
			  		this.setState({
			  			newTemplateAdded: true
			  		})
			  	}.bind(this),
			});
		}
	}

	actionsFormatter(cell, row) {
		var moveUpPopover = (
      		<Popover id="modal-popover" title="Move Template Up In Repricing Order">
        		Move this template up in repricing order if you want it to be applied BEFORE other templates.
      		</Popover>
		)

		var moveDownPopover = (
      		<Popover id="modal-popover" title="Move Template Down In Repricing Order">
        		Move this template down in repricing order if you want it to be applied AFTER other templates.
      		</Popover>
		)

		var instaPricePopover = (
      		<Popover id="modal-popover" title="Instant Repricing">
        		Click this button to reprice your inventory using this template immediately.
      		</Popover>
		)

	  	return (
	  		<div>
	            <a href="/edit_strategy"><Button bsStyle="default btn-sm margin-right"Edit</Button></a>
	            <OverlayTrigger placement="left" overlay={instaPricePopover}><Button bsStyle="default btn-sm margin-right">InstaPrice!</Button></OverlayTrigger>
	            <OverlayTrigger placement="left" overlay={moveUpPopover}><Button bsStyle="default btn-sm margin-right"><i className="fa fa-arrow-up"></i></Button></OverlayTrigger>
	            <OverlayTrigger placement="left" overlay={moveDownPopover}><Button bsStyle="default btn-sm margin-right"><i className="fa fa-arrow-down"></i></Button></OverlayTrigger>

	  		</div>
	  	)
	}


	render() {
		var table = (
			<BootstrapTable data={this.state.templates} multiColumnSearch={true} striped={true} bordered={false} hover={true}>
				<TableHeaderColumn isKey={true} dataAlign="center" dataField="name" editable={false}>Template Name</TableHeaderColumn>
				<TableHeaderColumn dataAlign="center" dataField="status" editable={false}>Status</TableHeaderColumn>
				<TableHeaderColumn dataAlign="center" dataField="last_updated" editable={false}>Last Updated</TableHeaderColumn>
				<TableHeaderColumn dataAlign="center" dataField="" dataFormat={this.actionsFormatter} editable={false}>Actions</TableHeaderColumn>
			</BootstrapTable>
		)

		if (!this.state.loaded) {
			table = (
				<div>
					<hr />
					<LoadingIndicator loadingText="Loading Templates... " />
				</div>
			)
		}

		var modalBody;
		var footerButtons;
		var newScheduleAddedNode;
		if (this.state.newTemplateAdded) {
			modalBody = (
				<Modal.Body>
					<h4>Congratulations! Your new schedule has been created.</h4>
				</Modal.Body>
			)
			footerButtons = (
				<Modal.Footer>
					<Button onClick={this.closeCreateTemplateModal.bind(this)}>Close</Button>
				</Modal.Footer>
			)
		} else {

			var formGroup;
			console.log("this is templatename");
			console.log(this.state.templateName);
			console.log(this.state.templateName.trim() === "")
			if (this.state.templateName.trim() === "") {
				formGroup = (
					<FormGroup controlId="formBasicText">
							<ControlLabel>Template Name</ControlLabel>
							<FormControl
							type="text"
							value={this.state.templateName}
							placeholder="Enter a unique template name!"
							onChange={this.handleTemplateNameChange.bind(this)}
							/>
							<FormControl.Feedback />
			        </FormGroup>
			    )
			} else {
				formGroup = (
					<FormGroup controlId="formBasicText" validationState={this.validateTemplateName()}>
							<ControlLabel>Template Name</ControlLabel>
							<FormControl
							type="text"
							value={this.state.templateName}
							placeholder="Enter a unique template name!"
							onChange={this.handleTemplateNameChange.bind(this)}
							/>
							<FormControl.Feedback />
			        </FormGroup>
				)
			}


			modalBody = (
	          	<Modal.Body>
  				    <form>
  				    	{formGroup}
					</form>
		        </Modal.Body>
			)
			footerButtons = (
      				<Modal.Footer>
        				<Button onClick={this.closeCreateTemplateModal.bind(this)}>Close</Button>
        				<Button bsStyle="success" onClick={this.createTemplate.bind(this)}>Create Template & Set Strategy!</Button>
  					</Modal.Footer>
			)
		}

		return (
            <div className="hpanel">
                <div className="panel-heading hbuilt" style={ {"padding": "10px"} }>
                    <span className="left-pad">All Templates</span>
                    <hr />
                    <p style={ {fontWeight:300, marginTop:"3px"} } className="left-pad">These are the repricer templates you have created, in the exact order that they will be applied to your inventory items.</p>
                    <div className="left-pad">
                        <button className="btn btn-info" onClick={this.showCreateTemplateModal.bind(this)}>Create a New Template</button>
        				<Modal show={this.state.showCreateTemplateModal} onHide={this.closeCreateTemplateModal.bind(this)}>
          					<Modal.Header closeButton>
               			 		<h4 className="modal-title" style={{fontWeight:300, fontFamily:'Open Sans'}}>Create a New Template</h4>
	          				</Modal.Header>
	          				{modalBody}
	          				{footerButtons}

        				</Modal>
                    </div>
                    {table}
                </div>
            </div>
		)
	}
}