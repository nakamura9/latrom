import React from 'react';

const Heading = (props) => {
    var style = {
        backgroundColor: 'black',
        color: 'white',
        padding: '10px',
        borderLeft: '1px solid white'
    };
    return(
        <thead style={style}>
            <tr>
            <td style={{minWidth: '50px'}}></td>
                {this.props.fields.map((field, index) =>(
                    <td style={style} key={index} > {field} </td>
                ))}
            </tr>
        </thead>
    );
    }
}

export default Heading;