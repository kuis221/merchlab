import React from 'react';
import DesignersTable from './DesignersTable.jsx';
import DesignersSummary from './DesignersSummary.jsx';

export default class DesignersPage extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loaded: false,
            designers: []
        }
    }

    unassignDesignerFromClient(designerUsername) {
        var data = {
            designer_username: designerUsername
        }
        $.post("/unassign_designer_from_client/", data, function(result) {
            console.log(result);
            var designersLeft = [];
            for (var c=0; c<this.state.designers.length; c++) {
                if (this.state.designers[c].designer_username !== designerUsername) {
                    designersLeft.push(this.state.designers[c]);
                }
            }
            this.setState({designers:designersLeft});
        }.bind(this));
    }

    componentDidMount() {
        this.serverRequest = $.get('/get_designers/', function (result) {
            var designers = JSON.parse(result);
            console.log(designers);
            this.setState({
                designers: designers,
                loaded: true
            });
        }.bind(this));    
    }

    updateTable(designer) {
        var designers = this.state.designers;
        designers.push(designer);
        this.setState({designers})

    }
    render() {
        return (
            <div>
                <div class="row">
                    <div className="col-lg-12" style={{padding:'0px'}}>
                        <DesignersSummary designers={this.state.designers} />
                        <br />
                        <DesignersTable 
                            designers={this.state.designers} 
                            updateTable={this.updateTable.bind(this)}
                            unassignDesignerFromClient={this.unassignDesignerFromClient.bind(this)}
                        />
                        <br />
                    </div>
                </div>
            </div>
        )
    }
}