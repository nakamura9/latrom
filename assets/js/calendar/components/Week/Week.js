import React from 'react';
import Day from '../Day/DayMonth';

const week = (props) => {
    let cellStyle = {
        borderCollapse:"collapse",
        border:"1px solid black"
    }
    return(
        <tr>
            {props.days.map((day, i) =>(
                <td key={i}
                    style={cellStyle}>
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