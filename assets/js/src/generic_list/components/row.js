import React from 'react';
import {DeleteButton} from '../../common';
/*Properties
    index for datarow object
    deleteHandler for delete button
    fieldOrder for datarow
    fields for datarow
*/

const dataRow = (props) =>{
    return(
        <tr>
            {props.fieldOrder.map((fieldName, i) =>(
                <td key={i}>{props.data[fieldName]}</td>
            ))}
            {props.hasLineTotal ?
            <td>
                {props.data.lineTotal}
            </td>
            : null}
            <td>
                <DeleteButton 
                    index={props.index}
                    handler={props.deleteHandler}/>
            </td>
        </tr>
    )
}

export default dataRow;