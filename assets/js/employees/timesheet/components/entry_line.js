import React from 'react';

const entryLine = (props) => {
    return(
        <tr>
           <td>{props.data.date}</td>
           <td>{props.data.timeIn}</td>
           <td>{props.data.timeOut}</td> 
           <td>{props.data.breaksTaken}</td>
           <td>{props.data.workingTime}</td>
           <td>
                <div className="button-group">
                        <button 
                        className="btn btn-info btn-sm"
                        onClick={() => props.editHandler(props.index)}>
                        <i className="fas fa-edit"></i>
                    </button>
                    <button 
                        className="btn btn-danger btn-sm"
                        onClick={() => props.deleteHandler(props.index)}>
                        <i className="fas fa-trash"></i>
                    </button>
                </div>
                
           </td>
        </tr>
    )
}

export default entryLine;