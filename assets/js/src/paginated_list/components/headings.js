import React from 'react';

const headings = (props) =>{
    return(
        <thead>
            <tr className="bg-primary">
                {props.headings.map((heading, i) =>(
                    <td>{heading}</td>
                ))}
                <td></td>
            </tr>
        </thead>
    )
}

export default headings;