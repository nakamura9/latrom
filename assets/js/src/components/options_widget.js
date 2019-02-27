import React, {Component} from "react";

const optionsWidget = (props) =>{
    let rendered;
    if(props.choices.length > 0){
        rendered = props.choices.map((item, i) => {
            //always display id and display field
            return(<div style={{color: "black"}} key={i} onClick={() => props.onSelectValue(i)}>
                    {item}
                </div>)
        });
    }else{
        rendered = (<div style={{color: "grey"}}>No results</div>)
    }

    return(
        <div style={{
            border: "1px solid grey",
            display: props.hidden ? "none" : "block",
            position:"absolute",
            width: "100%",
            zIndex: 1,
            backgroundColor: "#fff",
            maxHeight: "150px",
            overflowY: "auto",
            maxWidth: "300px",
            minWidth: "150px"
        }}>
            {rendered}
        </div>
    )
}


export default optionsWidget;