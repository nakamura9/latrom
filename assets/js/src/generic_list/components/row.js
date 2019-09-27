import React from 'react';
import {DeleteButton} from '../../common';
/*Properties
    index for datarow object
    deleteHandler for delete button
    fieldOrder for datarow
    fields for datarow
*/

const dataRow = (props) =>{
    const cellStyle = {
        border: '1px solid #ccc',
        borderCollapse: 'collapse',
        textAlign: 'center'
    }
    
    return(
        <tr>
            {props.fieldOrder.map((fieldName, i) =>(
                <td style={cellStyle} key={i}>{props.data[fieldName]}</td>
            ))}
            {props.hasLineTotal ?
            <td style={cellStyle}>
                {props.data.lineTotal}
            </td>
            : null}
            <td style={cellStyle}>
                <DeleteButton 
                    index={props.index}
                    handler={props.deleteHandler}/>
            </td>
        </tr>
    )
}

export default dataRow;