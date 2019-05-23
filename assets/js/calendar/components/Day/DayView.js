import React, {Component} from 'react';
import Event from '../Event';
import axios from 'axios';
import Day from './Day';
import styles from './Day.css';

class DayView extends Component{
    state = {
        date: "",
        events: [],
        width: 640
    }

    componentDidMount(){
        this.props.linkUpdater();
        const params = this.props.match.params 
        axios({
            method: 'GET',
            url: `/planner/api/calendar/day/${params.year}/${params.month}/${params.day}`
        }).then(res =>{
            this.setState({
                events: res.data.events.events,
                date: res.data.date
            })
        })
        const windowWidth = document.documentElement.clientWidth;
        const sidebarWidth = document.getElementById('sidebar').offsetWidth;
        const calendarWidth = windowWidth - sidebarWidth - 5;
        this.setState({width: calendarWidth})
    }

    render(){
    const intervals = ['00:00', '01:00', '02:00', '04:00', '05:00', '06:00', 
    '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', 
    '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00',
    '21:00', '22:00', '23:00'  
    ]
    // only week and day views have an hourly breakdown therefore only two 
    // options
    const hourByHour = 
        (<table style={{
            width: `${this.state.width - 40}px`,
            position: "absolute",
            top:  "90px",
            left: "0px"
        }}>
            <tbody>
                {intervals.map((time, i) =>(
                    <tr 
                        height={20}
                        key={i} 
                        style={{
                        borderTop: "1px solid #aaaaaa",
                        minHeight: "20px",
                        
                    }}>
                        <td style={{width: "20%"}}>{time}</td>
                        <td style={{
                            width: "80%",
                        }}>&nbsp;</td>
                    </tr>
                ))}
            </tbody>
        </table>);
    
        const dayWrapper = {
            width: `${this.state.width - 20}px`,
            height: '500px',
           
            padding: '0px',
            overflowY: 'auto'
        } 
        const dayLabel = 
        <h1 style={{
            color: 'white',
            backgroundColor: '#07f',
            padding: '30px',
            clear: "both",
            float: "left",
            width: "100%"        
        }}>{this.state.date}</h1>
        // do some overlap detection
        return(
            <div style={dayWrapper}>
            
            <div style={{
                clear:'both',
                width:'100%',
                height:'30px',
                }}>
                {dayLabel}
            </div>
            <div 
                style={{
                    position: "relative",
                    width: `${this.state.width -40}px`,//here
                    height:  "640px",
                }}>
            {hourByHour}
            {this.state.events.map((event, i) =>(
                <Event
                    index={1 + i}
                    offset={250 * (i % 3)}
                    width={this.state.width}
                    key={i} 
                    data={event}
                    view={"day"}/>
            ))}
            </div>
        </div>
    )
    }    
}

export default DayView;