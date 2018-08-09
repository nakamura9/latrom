import React from 'react';
import Day from './Day/Day';

const week = (props) => {
    let cellStyle = {
        borderCollapse:"collapse",
        border:"1px solid black"
    }
    if(props.days.length === 7){
        return(
            <tr>
                {props.days.map((day, i) =>(
                    <td key={i}
                        style={cellStyle}>
                        <Day data={day} />
                    </td>
                ))}
            </tr>
        )
    }else{
        return<tr>
            <td>Still Loading</td>
        </tr>
    }
    
}

export default week;