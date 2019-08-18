import React from 'react';

const leave = (props) =>{    
    let startY = 90;
    let height = 22;
    
    if(props.data.start_date){
            const start = parseInt(props.data.start_date);
            const end = parseInt(props.data.end_date);

            startY = 90 + (start * 22);
            // for errors in recording the event times
            if(end > start){
                height = (end - start) * 22;
            }
    }
    
    let style = {
        margin: '2px',
        padding: '5px',
        height: "100%",
        width: "100%",
        color: 'white',
        backgroundColor: '#07f',
        zIndex: 1,
        position: "absolute",
        left: `${40 + props.offset}px`,
        border: '1px solid white',
        top: `${startY}px`,
        height: `${height}px`, 
        width: "150px",
    };
    return(
        <a 
            href={"/employees/leave-detail/" + props.data.id}>
            <div style={style}>
                <div>
                    <i className={"fas fa-user"}></i>
                    <span style={{margin: "0px 5px"}}>{props.data.employee}</span>
                </div>
            </div>
        </a>
    );
}

export default leave;