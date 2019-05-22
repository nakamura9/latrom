import React, {Component} from 'react';
import axios from 'axios'


class  MiniCalendar extends Component{
    state = {
        weeks: []
    }

    
    componentDidUpdate(prevProps, prevState){
        if(this.props.year !== prevProps.year || this.props.month !== this.props.month){
            axios({
                method: 'GET',
                url: `/planner/api/calendar/month/${this.props.year}/${this.props.month}`
            }).then(res =>{
                console.log(res.data)
                this.setState({
                    weeks: res.data.weeks,
                    period: res.data.period_string
                })
            })
        }
    }
    
    render(){
        return(
            <div>
            <h3 style={{color: "white"}}>{this.state.period}</h3>
            <table style={{
                border:'1px solid white', 
                margin: '5px', 
                padding: '20px',
                color: "white"
            }}>
                <tbody>
                    <tr>
                        <th>Mo</th>
                        <th>Tu</th>
                        <th>We</th>
                        <th>Th</th>
                        <th>Fr</th>
                        <th>Sa</th>
                        <th>Su</th>
                    </tr>
                    {this.state.weeks.length === 0
                        ? <tr>
                            <td colSpan={7}>Loading data...</td>
                        </tr>
                        : null
                    }
                    {this.state.weeks.map((week, i) =>(
                        <tr key={i}>

                            {week.map((day, j) =>(
                                <td key={j} style={{padding:'3px'}}>
                                    <a 
                                        href={`/calendar/day/${day.date}`}
                                        style={{
                                            textDecoration: "none",
                                        color: "white"
                                    }}>{day.day}</a></td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
            </div>
        );
    }
}



export default MiniCalendar;