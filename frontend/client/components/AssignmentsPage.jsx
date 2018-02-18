import React from 'react';
import AssignmentsSummary from './AssignmentsSummary.jsx';
import AssignmentsTable from './AssignmentsTable.jsx';

export default class AssignmentsPage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loaded: false,
            assignments: [],
            designers: [],
            showNewAssignmentModal: false
        }
    }


    componentDidMount() {
        this.serverRequest = $.get('/get_assignments/', function (result) {
            var data = JSON.parse(result);
            console.log(data);
            this.setState({
                assignments: data.assignments,
                designers: data.designers,
                loaded: true
            });
        }.bind(this));    
    }

    updateTable(assignment) {
        var assignments = this.state.assignments;
        console.log("this is the assignment", assignment);
        assignments.push(assignment);
        this.setState({assignments})

    }


    assignDesigner(id, designerUsername) {
        console.log(id, designerUsername, "being assigned");
        var assignments = this.state.assignments;
        for (var c=0; c<assignments.length; c++) {
            var assignment = assignments[c];
            console.log(assignment);
            if (assignment.id === id) {
                assignments[c].designer_username = designerUsername;
                assignments[c].status = "assigned";
                var data = {
                    designer_username: designerUsername,
                    assignment_id: id,
                    client_username: $("#client-username").text()
                }
                this.serverRequest = $.post('/assign_designer_to_assignment/', data, function (result) {
                    var data = JSON.parse(result);
                    console.log(data);
                }.bind(this));    
                c = assignments.length;
            }
        }
        this.setState({assignments})
    }

    unassignDesigner(id) {
        console.log(id, "unassigning");
        var assignments = this.state.assignments;
        for (var c=0; c<assignments.length; c++) {
            var assignment = assignments[c];
            console.log(assignment);
            if (assignment.id === id) {
                assignments[c].designer_username = null;
                assignments[c].status = "unassigned";
                var data = {
                    assignment_id: id,
                    client_username: $("#client-username").text()
                }
                this.serverRequest = $.post('/unassign_designer_from_assignment/', data, function (result) {
                    var data = JSON.parse(result);
                    console.log(data);
                }.bind(this));
                c = assignments.length;
            }
        }
        this.setState({assignments})
    }

    deleteAssignment(id) {
        this.serverRequest = $.post('/delete_assignment/', data, function (result) {
            var data = JSON.parse(result);
            console.log(data);
        }.bind(this));
        c = assignments.length;

        console.log(id, "unassigning");
        var assignments = this.state.assignments;
        var assignmentsLeft = [];
        for (var c=0; c<assignments.length; c++) {
            var assignment = assignments[c];
            console.log(assignment);
            if (assignment.id !== id) {
                assignmentsLeft.push(assignment);
            }
        }
        this.setState({assignments:assignmentsLeft})    
    }


    render() {
        return (
            <div>
                <div className="row">
                    <div className="col-lg-12">
                        <AssignmentsSummary designers={this.state.designers} />
                        <br />
                        <AssignmentsTable 
                            assignments={this.state.assignments}  
                            designers={this.state.designers} 
                            assignDesigner={this.assignDesigner.bind(this)}
                            unassignDesigner={this.unassignDesigner.bind(this)} 
                            updateTable={this.updateTable.bind(this)}
                        />
                    </div>
                </div>
            </div>
        )
    }
}