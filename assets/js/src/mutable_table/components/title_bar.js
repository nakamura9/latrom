import React from 'react';

const titleBar = (props) =>{
    return(<thead>
            <tr className="bg-primary text-white">
                {props.headings.map((heading, i)=>(
                    <td key={i}>{heading}</td>
                ))}
                <td></td>
            </tr>        
        </thead>)
};

export default titleBar;