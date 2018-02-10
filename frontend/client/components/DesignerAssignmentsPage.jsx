import React from 'react';
import AssignmentsSummary from './AssignmentsSummary.jsx';
import AssignmentsTable from './AssignmentsTable.jsx';

export default class DesignerAssignmentsPage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loaded: false,
            assignments: [],
        }
    }


    componentDidMount() {
        var clientUsername = $("#client-username").text();
        console.log(clientUsername);
        console.log("/va_assignments/" + clientUsername + "/data/");
        this.serverRequest = $.get('/va_assignments/' + clientUsername + '/data/', function (result) {
            var data = JSON.parse(result);
            console.log(data);
            this.setState({
                assignments: data.assignments,
                loaded: true
            });
        }.bind(this));    
    }

    render() {
        return (
            <div>
                <div className="row">
                    <div className="col-lg-12">
                        <AssignmentsTable 
                            assignments={this.state.assignments}  
                            isDesignerView={true} 
                        />
                    </div>
                </div>
            </div>
        )
    }
}