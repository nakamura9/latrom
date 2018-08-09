import React from 'react';
import Week from './Week';

const month = (props) =>{
    return(
        <table>
            <tbody>
            {props.weeks.map((week, i)=>(
                <Week key={i} days={week} />
            ))}
            </tbody>
        </table>
    );
}

export default month;