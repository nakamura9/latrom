import React, {Component} from 'react';
import Week from '../Week/Week';
import {Aux} from '../../../src/common';
import axios from 'axios';
import styles from './month.css';

class Month extends Component{
    state = {
        weeks: [],
        period: "",
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
        
        let contents = null;
        if(this.state.weeks.length === 0){
            contents = <h3>Loading Data...</h3>
        }else{
            contents = (<table>
                <thead>
                    <tr>
                        <th className={styles.header}>Monday</th>
                        <th className={styles.header}>Tuesday</th>
                        <th className={styles.header}>Wednesday</th>
                        <th className={styles.header}>Thursday</th>
                        <th className={styles.header}>Friday</th>
                        <th className={styles.header}>Saturday</th>
                        <th className={styles.header}>Sunday</th>
                    </tr>
                </thead>
                <tbody>
                {this.state.weeks.map((week, i)=>(
                    <Week 
                        width={this.props.width}
                        height={this.props.height}
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