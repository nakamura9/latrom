import React from 'react';

const shiftLine = (props) =>{
    return(
        <tr>
            <td>{props.data.shiftName}</td>
            <td>{props.data.startTime}</td>
            <td>{props.data.endTime}</td>
            <td><input 
                    className="form-control"
                    type="checkbox"
                    checked={props.data.monday} />
            </td>
            <td><input 
                    className="form-control"
                    type="checkbox"
                    checked={props.data.tuesday} />
            </td>
            <td><input 
                    className="form-control"
                    type="checkbox"
                    checked={props.data.wednesday} />
            </td>
            <td><input 
                className="form-control"
                type="checkbox"
                checked={props.data.thursday} />
            </td>
            <td><input 
                className="form-control"
                type="checkbox"
                checked={props.data.friday} />
            </td>
            <td><input 
                className="form-control"
                type="checkbox"
                checked={props.data.saturday} />
            </td>
            <td><input 
                className="form-control"
                type="checkbox"
                checked={props.data.sunday} />
            </td>
        </tr>
    )
};

export default shiftLine;