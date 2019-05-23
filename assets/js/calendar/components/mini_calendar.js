import React, {Component} from 'react';
import axios from 'axios'
import Radium from 'radium';
import styles from './mini_calendar.css';


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
            <h4 className={styles.title}>{this.state.period}</h4>
            <table className={styles.miniTable}>
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
                                    <a key={i.toString() + '-' + j.toString()}
                                        href={`/calendar/day/${day.date}`}
                                        style={{
                                            textDecoration: "none",
                                        color: (i==0 && day.day > 7) || (i == 4 && day.day < 7)
                                        ? '#007bff' 
                                        : 'white' ,
                                        width:" 100%",
                                        display: 'inline-block',
                                        ":hover": {
                                            color: '#007bff',
                                            backgroundColor: 'white'
                                        }
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



export default Radium(MiniCalendar);