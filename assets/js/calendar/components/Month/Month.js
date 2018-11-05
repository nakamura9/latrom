import React, {Component} from 'react';
import Week from '../Week/Week';
import {Aux} from '../../../src/common';
import axios from 'axios';

class Month extends Component{
    state = {
        weeks: [],
        period: ""
    }

    componentDidMount(){
        const params = this.props.match.params 
        axios({
            method: 'GET',
            url: `/planner/api/calendar/month/${params.year}/${params.month}`
        }).then(res =>{
            this.setState({
                weeks: res.data.weeks,
                period: res.data.period_string
            })
        })
    }

    render(){
        let cellStyle = {
            borderCollapse:"collapse",
            border:"1px solid black"
        };
        let contents = null;
        if(this.state.weeks.length === 0){
            contents = <h3>Loading Data...</h3>
        }else{
            contents = (<table>
                <thead>
                    <tr>
                        <th style={cellStyle}>Monday</th>
                        <th style={cellStyle}>Tuesday</th>
                        <th style={cellStyle}>Wednesday</th>
                        <th style={cellStyle}>Thursday</th>
                        <th style={cellStyle}>Friday</th>
                        <th style={cellStyle}>Saturday</th>
                        <th style={cellStyle}>Sunday</th>
                    </tr>
                </thead>
                <tbody>
                {this.props.weeks.map((week, i)=>(
                    <Week 
                        key={i} 
                        days={week}/>
                ))}
                </tbody>
            </table>);
        }
        return(
            <Aux>
            <h3>Month: {this.props.period}</h3>
            {contents}
            </Aux>
        );
    }
    
    
}

export default Month;