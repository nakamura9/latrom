import React from 'react';
const event = (props) =>{

    
    let startY = 90;
    let height = 44;
    
    if(props.view === "month"){
        startY = 0;
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
        margin: '2px',
        padding: '5px',
        height: "100%",
        width: "100%",
        color: 'white',
        backgroundColor: 'slateblue'
    };
    return(
        <a 
            style={{
                zIndex: 1,
                position: "absolute",
                left: props.view === "month" ? "0px" :"40px",
                top: `${startY}px`,
                height: `${height}px`,
                width: props.view === "day" 
                        ? "600px" : "200px",
                
            }} 
            href={"/planner/event-detail/" + props.data.id}>
            <div style={style}>
                <div>
                    <i className={"fas fa-" + props.data.icon}></i>
                    <span style={{margin: "0px 5px"}}>{props.data.label}</span>
                </div>
                {description}
                
            </div>
        </a>
    );
}

export default event;