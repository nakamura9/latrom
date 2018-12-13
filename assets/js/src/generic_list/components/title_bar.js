import React from 'react';
/* Props 
fieldOrder an array of field names
 */

const titleBar = (props) =>{
    
    return(
        <thead>
            <tr 
                className="bg-primary text-white"
                >
                {props.fieldOrder.map((fieldName, i)=>(
                    <th key={i}
                        style={{
                            padding: "10px",
                            width: `${props.fields[i].width}%`
                        }}>
                        {fieldName}
                    </th>
                ))}
                {props.hasLineTotal ?
                <th style={{
                    padding: "10px",
                    width: `20%`
                }}>
                    {/** if line total then the sum of widths must be 70% */}
                    LineTotal
                </th>
                : null
            }
                {/* For Delete buttons */}
                <th style={{
                    width: `10%`
                }}>&nbsp;</th>
            </tr>
        </thead>
    )
}

export default titleBar;