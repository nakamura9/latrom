import React, {Component} from 'react';
import Day from '../Day/Day';
import {Aux} from '../../../src/common';
import axios from 'axios';
import styles from './week.css';

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
        if(this.state.days.lenght === 0){
            return(<h3>Loading data...</h3>)
        }
        const weekHeaderHeight = 42;
        const navBarHeight = document.getElementById('navbar').offsetHeight;
        const windowHeight = document.documentElement.clientHeight;
        const height = windowHeight - weekHeaderHeight - navBarHeight -43;
    
        return(
            <Aux>
                <h3 className={styles.weekHeader}>Week: {this.state.week}</h3>
               <div style={{
                maxHeight: (height + 35) + "px",
                overflowY: "auto",
                width: '79vw'
                }}>
                    <table>
                        <thead>
                            <tr>
                                <th className={styles.headStyle}>Monday</th>
                                <th className={styles.headStyle}>Tuesday</th>
                                <th className={styles.headStyle}>Wednesday</th>
                                <th className={styles.headStyle}>Thursday</th>
                                <th className={styles.headStyle}>Friday</th>
                                <th className={styles.headStyle}>Saturday</th>
                                <th className={styles.headStyle}>Sunday</th>
                            </tr>
                        </thead>
                        <tbody >
                            <tr>
                                {this.state.days.map((day, i) =>(
                                    <td key={i}
                                        className={styles.cellStyle}
                                        >
                                        <div >
                                            <Day data={day} view={'week'} width={this.props.width} height={height}/>
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