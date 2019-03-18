import React, {Component} from 'react';
import Day from '../Day/Day';
import {Aux} from '../../../src/common';
import axios from 'axios';

class WeekView extends Component{
    state = {
        week: "",
        days: []
    }

    componentDidMount(){
        this.props.linkUpdater();
        const params = this.props.match.params 
        axios({
            method: 'GET',
            url: `/planner/api/calendar/week/${params.year}/${params.month}/${params.day}`
        }).then(res =>{
            this.setState({
                days: res.data.days,
                week: res.data.period_string
            })
        })
    }

    render(){
        const cellStyle = {
            borderCollapse:"collapse",
            border:"1px solid black",
            
        };
        const headStyle = {
            ...cellStyle,
            color: "white",
            backgroundColor: "#007bff",
            padding: "10px"
            
        };
        if(this.state.days.lenght === 0){
            return(<h3>Loading data...</h3>)
        }
        return(
            <Aux>
                <h3 style={{
                    color: "white",
                    backgroundColor: "#007BfF",
               }}>Week: {this.state.week}</h3>
               <div style={{
                maxHeight: "500px",
                overflowY: "auto",
                minWidth: `${window.screen.width -250}px`
                }}>
                    <table>
                        <thead>
                            <tr>
                                <th style={headStyle}>Monday</th>
                                <th style={headStyle}>Tuesday</th>
                                <th style={headStyle}>Wednesday</th>
                                <th style={headStyle}>Thursday</th>
                                <th style={headStyle}>Friday</th>
                                <th style={headStyle}>Saturday</th>
                                <th style={headStyle}>Sunday</th>
                            </tr>
                        </thead>
                        <tbody >
                            <tr>
                                {this.state.days.map((day, i) =>(
                                    <td key={i}
                                        style={{...cellStyle, height: '640px'}}>
                                        <div >
                                            <Day data={day} view={'week'} width={this.props.width}/>
                                        </div>                                
                                    </td>
                                ))}
                            </tr>    
                        </tbody>
                    </table>
               </div> 
               
            </Aux>
        )
    }
}
    

export default WeekView;