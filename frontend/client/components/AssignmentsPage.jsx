import React from 'react';
import AssignmentsSummary from './AssignmentsSummary.jsx';
import AssignmentsTable from './AssignmentsTable.jsx';
import NewAssignmentPanel from './NewAssignmentPanel.jsx';

export default class AssignmentsPage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loaded: false,
            assignments: []
        }
    }


    componentDidMount() {
        this.serverRequest = $.get('/get_assignments/', function (result) {
            var assignments = JSON.parse(result);
            console.log(assignments);
            this.setState({
                assignments: assignments,
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
    render() {
        return (
            <div>
                <div class="row">
                    <div className="col-lg-12">
                        <AssignmentsTable assignments={this.state.assignments} />
                    </div>
                    <div className="col-lg-3">
                        <NewAssignmentPanel updateTable={this.updateTable.bind(this)} />
                    </div>
                </div>
            </div>
        )
    }
}