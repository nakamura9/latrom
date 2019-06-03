import React from 'react';
import Day from '../Day/DayMonth';
import styles from './week.css';

const week = (props) => {
    
    return(
        <tr>
            {props.days.map((day, i) =>(
                <td key={i}
                    className={styles.cellStyle}>
                    <Day 
                        width={props.width}
                        height={props.height}
                        data={day} 
                        view='month'/>
                </td>
            ))}
        </tr>
    )
    
}

export default week;