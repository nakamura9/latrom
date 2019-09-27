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
                    padding: "0px 10px",
                    ":hover": {
                        'color':'white',
                        'backgroundColor':'#007bff'
                    }
                }} key={i} onClick={() => this.props.onSelectValue(i)}>
                        {item.split('-')[1]}
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

            <div style={linkStyle} >
                <button onClick={this.props.closeDropdown}
                        type="button"
                        className="btn btn-sm">
                            <i className="fas fa-times"></i>
                </button>
            </div>
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