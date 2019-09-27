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
                return(item[this.props.idField ? this.props.idField : "id"] + " - " + item[this.props.nameField ? this.props.nameField : "name"])
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

    onSelectValue = (index) => {
        this.setState({
            selectedValue: this.state.filteredChoices[index],
            inputValue: this.state.filteredChoices[index],
            optionsHidden: true
        }, () => {
            this.props.addItem(this.state.selectedValue)
            this.setState({
                inputValue: "",
                selectedValue: ""
            })
        });
    }

    toggleOptions = () =>{
        this.setState((prevState) =>({
            optionsHidden: !prevState.optionsHidden
        }))
    }

    render(){
        const containerStyle = {
            padding: "3px",
            backgroundColor: "white",
            borderRadius: "3px",
            border: "1px solid #007bff"
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
                onFocus={() => this.setState({optionsHidden: false})}
                placeholder="Select item..."
                value={this.state.inputValue}
                onChange={this.inputChangeHandler}
                type="text"
                style={inputStyle} />
            <button 
                style={buttonStyle}
                type="button"
                onClick={this.toggleOptions}><i className="fas fa-angle-down"></i></button>
            </div>
            <OptionsWidget 
                closeDropdown={() =>this.setState({optionsHidden: true})}
                choices={this.state.filteredChoices}
                onSelectValue={this.onSelectValue}
                newLink={this.props.newLink}
                hidden={this.state.optionsHidden}/>
        </div>)
    }
}

export default SearchableTextInputWidget;