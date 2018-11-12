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
        this.props.linkUpdater();
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
        const cellStyle = {
            borderCollapse:"collapse",
            border:"1px solid black"
        };
        const headStyle = {
            ...cellStyle,
            color: "white",
            backgroundColor: "#07f",
            padding: "10px"
            
        };
        let contents = null;
        if(this.state.weeks.length === 0){
            contents = <h3>Loading Data...</h3>
        }else{
            contents = (<table>
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
                <tbody>
                {this.state.weeks.map((week, i)=>(
                    <Week 
                        key={i} 
                        days={week}/>
                ))}
                </tbody>
            </table>);
        }
        return(
            <Aux>
            {contents}
            </Aux>
        );
    }
    
    
}

export default Month;