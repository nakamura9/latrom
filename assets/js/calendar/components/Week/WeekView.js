import React from 'react';
import Day from '../Day/Day';
import {Aux} from '../../../src/common';

const weekView = (props) =>{
    let cellStyle = {
        borderCollapse:"collapse",
        border:"1px solid black"
    };
    return(
        <Aux>
            <h3>Week: {props.period}</h3>
            <table>
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
                    <tr>
                        {props.days.map((day, i) =>(
                            <td key={i}
                                style={cellStyle}>
                                <Day data={day} view={'week'}/>
                            </td>
                        ))}
                    </tr>    
                </tbody>
            </table>
        </Aux>
    )
}

export default weekView;