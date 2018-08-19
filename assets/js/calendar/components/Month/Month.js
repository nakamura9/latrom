import React from 'react';
import Week from '../Week/Week';
import {Aux} from '../../../src/common';

const month = (props) =>{
    let cellStyle = {
        borderCollapse:"collapse",
        border:"1px solid black"
    };
    let contents = null;
    if(props.weeks.length === 0){
        contents = <h3>Loading Data...</h3>
    }else{
        contents = (<table>
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
            {props.weeks.map((week, i)=>(
                <Week 
                    key={i} 
                    days={week}/>
            ))}
            </tbody>
        </table>);
    }
    return(
        <Aux>
        <h3>Month: {props.period}</h3>
        {contents}
        </Aux>
    );
}

export default month;