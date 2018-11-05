import React, {Component} from 'react';
import Event from '../Event';

class DayView extends Component{
    state = {
        date: "",
        events: []
    }

    componentDidMount(){

    }
    render(){
        let dayWrapper = {
            width: '350px',
            height: '500px',
            margin: 'auto',
            padding: '10px',
            border: '1px solid black'
        } 
        let dayHeader = {
            textAlign:'center',
            backgroundColor: 'slateblue',
            borderBottom: '1px solid black',
            color: 'white',
            padding: '5px'
        }
    
        return(
            <div style={dayWrapper}>
                <div style={dayHeader}>
                    <span >
                        <h1>{this.state.date}</h1>
                    </span>
                </div>
                <div>
                    {this.state.events.map((event, i) =>(
                        <Event key={i} data={event}/>
                    ))}
                </div>
            </div>
        )
    }    
}

export default DayView;