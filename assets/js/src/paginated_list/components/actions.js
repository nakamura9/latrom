import React from 'react';

const action = (props) =>{
    const container = {
        position: 'relative',
        display: 'block',
    }
    const content = {
        padding: '10px',
        display: 'none',
        minWidth: '100px',
        zIndex: 1,
        position: 'absolute',
        background: 'white'
    }
    const link = {
        textDecoration: 'none',
        color: 'black',
        padding: '5px'
    }
    return(<div >
                <button 
                    className="btn btn-secondary"
                    onClick={() =>{
                        //implement toggling of content
                    }}>Actions</button>
                <div style={content} id={`${props.id}_content`}>
                    {props.actionData.map((action, i)=>(
                        <a style={link} href={`${action.url}/${props.id}`}>{action.name}</a>
                    ))}
                </div>
            </div>)
}

export default action;