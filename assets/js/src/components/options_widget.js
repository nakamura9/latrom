import React, {Component} from "react";
import Radium from 'radium';
class OptionsWidget extends Component{
    
    openPopup = () =>{
        let modal = document.getElementById('id-my-modal');
        let popup = document.getElementById('popup-frame');

        popup.setAttribute('src', this.props.newLink);
        modal.style.display = 'block';
        modal.addEventListener()
    }
    
    render(){
        let rendered;
        if(this.props.choices.length > 0){
            rendered = this.props.choices.map((item, i) => {
                //always display id and display field
                return(<div style={{
                    color: "black",
                    ":hover": {
                        'color':'white',
                        'backgroundColor':'blue'
                    }
                }} key={i} onClick={() => this.props.onSelectValue(i)}>
                        {item}
                    </div>)
            });
        }else{
            rendered = (<div style={{color: "grey"}}>No results</div>)
        }

        const linkStyle = {
            padding: "5px 2px",
            color: "#007bff",
            borderBottom: '1px solid #aaa'
        }
        return(
            <div style={{
                border: "1px solid grey",
                display: this.props.hidden ? "none" : "block",
                position:"absolute",
                width: "100%",
                zIndex: 1,
                boxShadow: "0px 5px 20px grey",
                backgroundColor: "#fff",
                maxWidth: "300px",
                minWidth: "150px"
            }}>
            
            {this.props.newLink ? 
                <div onClick={this.openPopup} style={linkStyle}>Create new</div>
                : null
            }
                <div style={{
                    maxHeight: "150px",
                    overflowY: "auto",}}>
                {rendered}
                    
                </div>
            </div>
        )
    }
}


export default Radium(OptionsWidget);