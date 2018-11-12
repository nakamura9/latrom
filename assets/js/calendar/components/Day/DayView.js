import React, {Component} from 'react';
import Event from '../Event';
import axios from 'axios';
import Day from './Day';

class DayView extends Component{
    state = {
        date: "",
        events: []
    }

    componentDidMount(){
        this.props.linkUpdater();
        const params = this.props.match.params 
        axios({
            method: 'GET',
            url: `/planner/api/calendar/day/${params.year}/${params.month}/${params.day}`
        }).then(res =>{
            console.log(res.data);
            this.setState({
                events: res.data.events.events,
                date: res.data.date
            })
        })
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
            <Day 
                data={{
                    events: this.state.events,
                    date: this.state.date
                }}
                view="day"/>
        )
    }    
}

export default DayView;