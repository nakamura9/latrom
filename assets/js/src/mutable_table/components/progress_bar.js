import React from 'react';

const progressBar = (props) =>{
    const itemCount = props.data.length;
    const verifiedCount = props.data.filter((item) =>(item.verified)).length;

    let percentage = 100;
    if(itemCount > 0){
        percentage = (verifiedCount / itemCount) * 100;
    }
    percentage = percentage.toFixed(2);

    const backgroundStyle = {
        width: "100%", 
        minHeight: "30px", 
        border: "1px solid #777", 
        color: "#ddd"};

    const barStyle = {
        backgroundColor: "#00ff00",
        height: "30px",
        width: `${percentage}%`
    }
    return(
        <div style={{width: "100%"}}>
            <div><h5 style={{textAlign:"center"}}>Table Completion: {percentage}%</h5></div>
            <div style={backgroundStyle}>
                <div style={barStyle}>
                </div>
            </div>
        </div>
    )
}

export default progressBar;