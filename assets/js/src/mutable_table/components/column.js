import React from 'react';

const column = (props) => {
    if(props.field.mutable){
        if(props.field.widget){
            console.log(props.rowID)
            return(<td>
                {props.field.widgetCreator(props.root, props.rowID)}
            </td>)
        }else{
            return(
                <td>
                    <input 
                    type="number" 
                    className="form-control"
                    value={props.data}
                    onChange={props.inputHandler}
                    name={props.columnID}/>
                </td>
                );
        }
        
    }else{
        return(
            <td>
                {props.data}
            </td>
        )
    }
    
}

export default column;