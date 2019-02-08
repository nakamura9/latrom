import React from 'react';
import Column from './column'
/**
 * A row takes a list of fields and iterates over them 
 * returning a list of cells that populate it.
 * Each cell may be mutable or immutable based on the input 
 * 
 */
const row = (props) =>{
    return(
        <tr>
            {props.fields.map((field, i) =>(
                <Column 
                    key={i}
                    inputHandler={props.inputHandler}
                    data={props.fieldData[field.name]}
                    field={props.fields[i]}
                    root={props.root}
                    columnID={`${props.rowID}__${field.name}`} />
            ))}
        </tr>
    )
};

export default row;
