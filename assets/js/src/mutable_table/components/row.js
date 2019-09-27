import React from 'react';
import Column from './column'
/**
 * A row takes a list of fields and iterates over them 
 * returning a list of cells that populate it.
 * Each cell may be mutable or immutable based on the input 
 * 
 */
const row = (props) =>{
    const icon = props.fieldData.verified ? "edit" : "check";
    return(
        <tr>
            {props.fields.map((field, i) =>(
                <Column 
                    key={i}
                    inputHandler={props.inputHandler}
                    data={props.fieldData[field.name]}
                    field={props.fields[i]}
                    root={props.root}
                    rowID={props.rowID}
                    columnID={`${props.rowID}__${field.name}`} />
            ))}
            <td><button 
                    type='button'
                    onClick={() =>props.toggle(props.rowID)}
                    className={
                        `btn btn-${props.fieldData.verified ? 'success' : 'primary'}`}>
                <i className={`fa fa-${icon}`} ></i>
            </button></td>
        </tr>
    )
};

export default row;
