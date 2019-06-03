import React from 'react';
import styles from './event.css';

const event = (props) =>{

    let startY = 90;
    let height = 44;
    
    if(props.view === "month"){
        startY = 0;
        height = 32;
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
  

    const startX = props.offset ? props.offset: 0;

    return(
        <a className={[styles.event, 'hvr-grow'].join(' ')}
            style={{
                zIndex: props.index,
                left: props.view === "month" ? "0px" :`${40 + startX}px`,
                top: `${startY}px`,
                height: `${height}px`,
                width: props.view === "day" 
                        ? "250px" : props.view === "week" ?
                         `${props.width - 40}px` : `100%` ,
                
            }} 
            href={"/planner/event-detail/" + props.data.id}>
            <div className={styles.eventBox}>
                <div>
                    <i className={"fas fa-" + props.data.icon}></i>
                    <span> {props.data.label}</span>
                </div>
                {description}
                
            </div>
        </a>
    );
}

export default event;