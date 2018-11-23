import React, { Component } from 'react'


const DayField = (props) => {
    const options = [...Array(31).keys()];
    return(<select 
                className="form-control"
                style={{
                    padding: "0px",
                    minWidth: "30px"
                }}
                name={props.name} 
                onChange={props.handler}>
            <option value selected={props.initial === ""}>-----</option>
            {options.map((opt, i) =>(
                <option 
                    value={i + 1 } 
                    key={i}
                    selected={props.initial === i + 1}
                    >{i + 1}</option>
            ))}
        </select>)
}

export default DayField;