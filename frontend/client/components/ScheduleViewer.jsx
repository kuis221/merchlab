import React from 'react';
import LoadingIndicator from './LoadingIndicator.jsx'
import { Modal, OverlayTrigger, Popover, Tooltip, Button, 
	FormGroup, FormControl, ControlLabel, Alert } from 'react-bootstrap';
import TimePicker from 'rc-time-picker';

export default class TemplateViewer extends React.Component {
	constructor(props) {
    	super(props);
	  	this.state = {
	  		loaded: false, 
	  		schedules: [], 
	  		templateNames: [], 
	  		showAddScheduleModal: false, 
	  		currentTemplateToSchedule: null,
	  		newScheduleAdded: false
	  	}
  	}

	componentDidMount() {
		this.serverRequest = $.get('/query_schedules', function (result) {
			console.log(result)
			result = JSON.parse(result)
			var schedules = result.schedules;
			var templateNames = result.template_names;
			this.setState({
				schedules: schedules,
				templateNames: templateNames,
				loaded: true
			});
		}.bind(this));
	}

	deleteSchedule(schedule, templateName) {
		// Be optimistic and hope it worked
		var schedules = this.state.schedules;
		var newSchedules = {};

		var templates = schedules[schedule]
		var newTemplates = [];
		for (var c = 0; c<templates.length; c++) {
			if (templates[c] !== templateName) {
				newTemplates.push(templates[c])
			}
		}
		if (newTemplates.length == 0) {
			delete schedules[schedule]
		} else {
			schedules[schedule] = newTemplates			
		}

		this.setState({
			schedules: schedules
		})
		
		$.ajax({
		  	type: "POST",
		  	url: "/delete_schedule",
		  	data: {schedule: schedule, templateName: templateName},
		  	success: function(newSchedules) {
		  		newSchedules = JSON.parse(newSchedules);
		  		console.log(newSchedules, "here")
		  		console.log("not updating state intentionally")
		  		// @TOOD: Alert user if schedule failed to delete
		  	}.bind(this),
		});
	}

	showAddScheduleModal() {
		this.setState({
			showAddScheduleModal: true
		})
	}

	closeAddScheduleModal() {
		this.setState({
			showAddScheduleModal: false,
			currentTemplateToSchedule: null,
			newScheduleAdded: false,
			warnings: false
		})
	}

	validateScheduleToAdd() {
		// @TODO: possibly need to add more rules to this soon
		if (!this.state.currentTemplateToSchedule || this.state.currentTemplateToSchedule.trim() == "") {
			return "Current template is empty or invalid.";
		}
		if (!this.state.currentScheduleTime || this.state.currentScheduleTime.trim() == "" || 
			this.state.currentScheduleTime.split(':').length != 2) {
			return "Current scheduled time is invalid.";
		}
		return true;
	}

	addSchedule() {
		console.log("ok")
		console.log(this.state.currentTemplateToSchedule)
		console.log(this.state.currentScheduleTime)
		var isValid = this.validateScheduleToAdd();
		console.log(isValid);
		if (this.validateScheduleToAdd() === true) {
			var data = {
				templateName: this.state.currentTemplateToSchedule,
				schedule: this.state.currentScheduleTime
			}

			$.ajax({
			  	type: "POST",
			  	url: "/add_schedule",
			  	data: data,
			  	success: function(newSchedules) {
			  		newSchedules = JSON.parse(newSchedules);
			  		console.log(newSchedules, "here")
			  		this.setState({
						warnings: null,
						newScheduleAdded: true,
						currentTemplateToSchedule: null,
						currentScheduleTime: null,
						schedules: newSchedules
			  		})
			  	}.bind(this),
			});
		} else {
			this.setState({
				warnings: isValid // isValid is actually string, if there was an error
			})
		}
	}

	handleTemplateNameChange() {
		this.setState({
			currentTemplateToSchedule: document.getElementById("templateNameSelect").value
		})
	}

	getDisabledMinutes(hour) {
		var disabled = [];
		for (var c=0; c<60; c++) {
			if (c%5 !== 0) {
				disabled.push(c)
			}
		}
		return disabled;
	}

	changeSchedule(e) {
		var hour = e.get("hour");
		var minute = e.get("minute");
		this.setState({
			currentScheduleTime: hour + ":" + minute
		})
	}

	render() {

		var scheduleNodes = []

		function compareSchedules(first, second) {  
			console.log("comapring");
		    var firstHour = parseInt(first.split(":")[0])
		    var firstMinute = parseInt(first.split(":")[1])

		    var secondHour = parseInt(second.split(":")[0])
		    var secondMinute = parseInt(second.split(":")[1])

		    if (firstHour == secondHour) {
		    	if (firstMinute == secondMinute) {
		    		return 0;
		    	} else if (firstMinute < secondMinute) {
		    		return -1;
		    	} else {
		    		return 1;
		    	}
		    } else if (firstHour < secondHour) {
		    	return -1;
		    } else {
		    	return 1;
		    }
		}  

		var schedulesArray = Object.keys(this.state.schedules).sort(compareSchedules);
		console.log("This is shceuldesArray");
		console.log(schedulesArray);
		console.log(Object.keys(this.state.schedules));
		for (var c=0; c < schedulesArray.length; c++) {
			var schedule = schedulesArray[c];
			var templates = this.state.schedules[schedule]
			console.log("break")
			console.log(templates, schedule);
			console.log(this.state.schedules);
			if (!templates || templates.length == 0) {
				continue;
			}
			console.log(templates, "hihi")
			var templateNameDisplays = []
			templates.map(function(templateName) {
		        templateNameDisplays.push(
		        	(<span>[<a href="#" onClick={this.deleteSchedule.bind(this, schedule, templateName)}>X</a>] {templateName}</span>)
		        )
		        templateNameDisplays.push(<br />)
			}.bind((this)))
			scheduleNodes.push(
                <div className="vertical-timeline-block">
                    <div className="vertical-timeline-icon navy-bg">
                        <i className="fa fa-calendar"></i>
                    </div>
                    <div className="vertical-timeline-content">
                        <div className="p-sm">
                            <span className="vertical-date pull-right"> {schedule} PST</span>

                            <h2 style={{fontWeight:300, fontSize:"15px", fontFamily:'Open Sans'}}>
                            	{templateNameDisplays}
                            </h2>
                        </div>
                    </div>
                </div>				
			)
		}


		var scheduleComponent = (
            <div className="v-timeline vertical-container animate-panel" data-child="vertical-timeline-block" data-delay="1">
            	{scheduleNodes}
            </div>
		)


		if (!this.state.loaded) {
			var scheduleComponent = (
				<div>
					<hr />
					<LoadingIndicator loadingText="Loading Schedules..." />
				</div>
			)
		}

		var templateNames = this.state.templateNames.slice();
		templateNames.unshift("All Templates");

		var templateChoiceOptions = (templateNames).map(function(name) {
			return (
        		<option value={name}>{name}</option>
			)
		})

		var templateSelect;

		if (this.state.currentTemplateToSchedule === null) {
			templateSelect = (
      			<FormControl componentClass="select" bsClass="form-control input-sm" placeholder="select" onChange={this.handleTemplateNameChange.bind(this)}>
					<option>Select a template...</option>
					{templateChoiceOptions}
				</FormControl>
			) 
		} else {
			templateSelect = (
      			<FormControl componentClass="select" bsClass="form-control input-sm" placeholder="select" onChange={this.handleTemplateNameChange.bind(this)}>
					{templateChoiceOptions}				
				</FormControl>
			)

		}

		var warnings;
		if (this.state.warnings && this.state.warnings.trim() !== "") {
			warnings = (
			  	<Alert bsStyle="warning" style={{"margin-bottom":"0px"}}>
			    	<strong>Uh Oh! </strong>{this.state.warnings}
			  	</Alert>
			)
		}

		var modalBody;
		var footerButtons;
		var newScheduleAddedNode;
		if (this.state.newScheduleAdded) {
			modalBody = (
				<Modal.Body>
					<h4>Congratulations! Your new schedule has been created.</h4>
				</Modal.Body>
			)
			footerButtons = (
				<Modal.Footer>
					<Button onClick={this.closeAddScheduleModal.bind(this)}>Close</Button>
				</Modal.Footer>
			)
		} else {
			modalBody = (
				<Modal.Body>
				    <form style={{marginBottom: "10px"}}>
						<FormGroup controlId="templateNameSelect">
  							<ControlLabel>Choose a Template</ControlLabel>
  							{templateSelect}
						</FormGroup>
  						<ControlLabel>Choose a Time <small style={{fontWeight:300, fontFamily: 'Open Sans'}}>(All items are repriced on PST time)</small></ControlLabel>
  						<br />
						<TimePicker showSecond={false} use12Hours={true} disabledMinutes={this.getDisabledMinutes} onChange={this.changeSchedule.bind(this)} />
						<br />
					</form>
					{warnings}
		        </Modal.Body>
			)
			footerButtons = (
				<Modal.Footer>
					<Button onClick={this.closeAddScheduleModal.bind(this)}>Close</Button>
					<Button bsStyle="success" onClick={this.addSchedule.bind(this)}>Add Schedule!</Button>
				</Modal.Footer>
			)
		}



		var addScheduleModal = (
			<Modal show={this.state.showAddScheduleModal} onHide={this.closeAddScheduleModal.bind(this)}>
				<Modal.Header closeButton>
			 		<h4 className="modal-title" style={{fontWeight:300, fontFamily:'Open Sans'}}>Add a New Reprice Schedule</h4>
				</Modal.Header>
				{modalBody}
				{footerButtons}
			</Modal>
		)



		return (
            <div className="hpanel">
                <div className="panel-heading hbuilt" style={ {"padding": "10px"} }>
                    <span className="left-pad">Active Schedules</span>
                    <hr />
	                <div className="text-center">
	                    <button className="btn btn-success" onClick={this.showAddScheduleModal.bind(this)}>Schedule a New Reprice</button>
	                </div>
	                {scheduleComponent}
	                {addScheduleModal}
                </div>
            </div>
		)
	}

}