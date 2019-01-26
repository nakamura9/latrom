import React, {Component} from "react";
import OptionsWidget from "../../components/options_widget";
import axios from "axios";

class SearchableTextInputWidget extends Component{
    state = {
        filteredChoices: [],
        choices: [],
        inputValue: "",
        selectedValue: "",
        optionsHidden: true
    }

    componentDidMount(){
        axios({
            method: "GET",
            url: this.props.dataURL
        }).then(res => {
            let newChoices = res.data.map((item) =>{
                return(item["id"] + " - " + item["name"])
            });

            this.setState({
                choices: newChoices,
                filteredChoices: newChoices
            });
        })
    }

    inputChangeHandler = (evt) =>{
        let selectedValue = "";

        let filtered = this.state.choices.filter((val) =>(
            val.indexOf(evt.target.value) !== -1
        ))

        //checking if the selected value is in the list of options
        let index = this.state.choices.indexOf(evt.target.value);
        
        if(index !== -1){
            selectedValue = evt.target.value;
        }

        this.setState({
            filteredChoices: filtered,
            inputValue: evt.target.value,
            selectedValue: selectedValue,
            optionsHidden: selectedValue !== "" 
        });
    }

    addItemToSelectedItems = () =>{
        if(this.state.selectedValue !== ""){
            this.props.addItem(this.state.selectedValue)
        }
    }

    onSelectValue = (index) => {
        this.setState({
            selectedValue: this.state.filteredChoices[index],
            inputValue: this.state.filteredChoices[index],
            optionsHidden: true
        });
    }

    render(){
        const containerStyle = {
            padding: "3px",
            backgroundColor: "white",
            borderRadius: "3px",
        };
        const inputStyle = {
            width:"85%", 
            border: "0px",
        };
        const buttonStyle = {
            width:"15%",
            backgroundColor: "white",
            border: "0px"
        };
        
        return(<div style={containerStyle}>
            <div>
                <input 
                placeholder="Select item..."
                value={this.state.inputValue}
                onChange={this.inputChangeHandler}
                type="text"
                style={inputStyle} />
            <button 
                style={buttonStyle}
                type="button"
                onClick={this.addItemToSelectedItems}><i className="fas fa-plus"></i></button>
            </div>
            <OptionsWidget 
                choices={this.state.filteredChoices}
                onSelectValue={this.onSelectValue}
                hidden={this.state.optionsHidden}/>
        </div>)
    }
}

export default SearchableTextInputWidget;