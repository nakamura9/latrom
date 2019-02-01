import React from 'react';

const column = (props) => {
    return(
        <td>
            {props.mutable ?  <input 
                                type="number" 
                                className="form-control"
                                value={props.data}
                                onChange={props.inputHandler}
                                name={props.columnID}/>
                            :  props.data
                            }
        </td>
    )
}

export default column;