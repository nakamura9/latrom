import React from "react";
import SelectedItem from "./list_item";

const selectedItemsListWidget = (props) =>{
    const containerStyle = {
            maxHeight: "150px",
            overflowY: "auto",
            marginBottom: "5px"
        };
    
    return(
        <div style={containerStyle}>
            {props.selectedItems.map((item, i) =>(
                <SelectedItem 
                    key={i}
                    removeHandler={props.removeHandler}
                    value={item}
                    index={i} />
            ))}
        </div>
    )
}

export default selectedItemsListWidget;