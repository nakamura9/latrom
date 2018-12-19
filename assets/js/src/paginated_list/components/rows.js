import React from 'react';
import Action from './actions';

const row = (props) =>{
    return(
        <tr>
            {props.rowFields.map((element, i)=>(
                <td key={i}>{props.rowData[element]}</td>
            ))}
            <td>
                <Action 
                    actionData={props.actionData}
                    id={props.rowData.id}/>
            </td>
        </tr>
    )
}

export default row;