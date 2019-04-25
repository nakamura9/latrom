import React, {Component} from "react";

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
                return(<div style={{color: "black"}} key={i} onClick={() => this.props.onSelectValue(i)}>
                        {item}
                    </div>)
            });
        }else{
            rendered = (<div style={{color: "grey"}}>No results</div>)
        }

        const linkStyle = {
            padding: "5px 2px",
            color: "#007bff",
        }
        return(
            <div style={{
                border: "1px solid grey",
                display: this.props.hidden ? "none" : "block",
                position:"absolute",
                width: "100%",
                zIndex: 1,
                backgroundColor: "#fff",
                maxHeight: "150px",
                overflowY: "auto",
                maxWidth: "300px",
                minWidth: "150px"
            }}>
            
            {this.props.newLink ? 
                <div onClick={this.openPopup} style={linkStyle}>Create new</div>
                : null
            }
                {rendered}
            </div>
        )
    }
}


export default OptionsWidget;