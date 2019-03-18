import React from 'react';
const event = (props) =>{

    
    let startY = 90;
    let height = 44;
    
    if(props.view === "month"){
        startY = 0;
        height = 30;
    }else{
        if(props.data.start){
            const start = parseInt(props.data.start.split(":")[0]);
            const end = parseInt(props.data.end.split(":")[0]);

            startY = 90 + (start * 22);
            // for errors in recording the event times
            if(end > start){
                height = (end - start) * 22;
            }
            
        }
    }
    
    

    let description = null;
    if (props.description){
        description = (<div>
                        <p>{props.description}</p>
                    </div>);
        }
    let style = {
        height: "100%",
        width: "100%",
        color: 'white',
        backgroundColor: '#007bff',
        padding: '5px'
    };

    const startX = props.offset ? props.offset: 0;

    return(
        <a 
            style={{
                zIndex: props.index,
                position: "absolute",
                left: props.view === "month" ? "0px" :`${40 + startX}px`,
                top: `${startY}px`,
                border: '1px solid white',
                height: `${height}px`,
                textDecoration: 'none',
                width: props.view === "day" 
                        ? "250px" : `${props.width - 40}px` ,
                
            }} 
            href={"/planner/event-detail/" + props.data.id}>
            <div style={style}>
                <div>
                    <i className={"fas fa-" + props.data.icon}></i>
                    <span style={{marginLeft: '2px'}}>{props.data.label}</span>
                </div>
                {description}
                
            </div>
        </a>
    );
}

export default event;