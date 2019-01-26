import React, {Component} from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import OptionsWidget from "./options_widget";

// TODO make sure that on clear works, replace caret with times when deleting data
class SearchableWidget extends Component {
    //currValue is whats being typed, selected is the value validated
    state = {
        filteredChoices: [],
        choices: [],
        currValue: "",
        selectedValue: "",
        optionsHidden: true
    }

    componentDidUpdate(prevProps, prevState){
        if (this.props.list &&  this.props.list.length != prevProps.list.length){
            this.setState({
                currValue: "",
                selectedValue: ""
            })
            //remove selected choice from list of choices 
        }
    }

    componentDidMount(){
        axios({
            method: "GET",
            url: this.props.dataURL
        }).then(res => {
            let newChoices = res.data.map((item) =>{
                return(item[this.props.idField] + " - " + item[this.props.displayField])
            });

            this.setState({
                choices: newChoices,
                filteredChoices: newChoices
            });
        })
    }

    onSelectValue = (index) => {
        this.setState({
            selectedValue: this.state.filteredChoices[index],
            currValue: this.state.filteredChoices[index],
            optionsHidden: true
        });
        this.props.onSelect(this.state.filteredChoices[index]);
    }

    toggleOptions = () =>{
        // only toggle options if the value is not already selected
        if(this.state.selectedValue){
            this.clearValue()
        }else{
            this.setState((prevState) =>({
                optionsHidden: !prevState.optionsHidden
            }))
        }
        
    }

    clearValue = () =>{
        this.setState({
            currValue: "",
            selectedValue: "",
        });
        this.props.onClear();
    }

    handleChange = (evt) => {
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
            currValue: evt.target.value,
            selectedValue: selectedValue,
            optionsHidden: selectedValue !== "" 
        });

        if(index !== -1){
            this.props.onSelect(evt.target.value);
        }
    }
    render(){
        
        return(
            <div style={{
                margin: "2px",
                position:"relative",
                display: "inline-block"
                }}>
                <TextBoxWidget 
                    currValue={this.state.currValue}
                    validChoice={this.state.selectedValue}
                    handleChange={this.handleChange}
                    toggleOptions={this.toggleOptions}/>
                   
                <OptionsWidget 
                    choices={this.state.filteredChoices}
                    onSelectValue={this.onSelectValue}
                    hidden={this.state.optionsHidden}/>
            </div>
        );
    }
}


class TextBoxWidget extends Component{
    render(){
        let icon;
        if(this.props.validChoice === ""){
            icon = "fa-angle-down"
        }else{
            icon = "fa-times"
        }
        return(<div style={{padding: "3px", backgroundColor: "white", borderRadius: "2px"}}>
        <input 
            type="text"
            value={this.props.currValue}
            onChange={this.props.handleChange}
            placeholder="Select item..."
            style={{
                padding: "3px",
                border: "0px",
                width:"85%",
                backgroundColor: this.props.validChoice === "" ?
                    "#fff" : "#aaf"
        }}/>
        <button style={{
            width: "15%",
            height: "100%",
            border: "0px",
            backgroundColor: "#fff",
        }} 
        onClick={this.props.toggleOptions}>
            <i className={`fas ${icon}`}></i>
        </button>
    </div>)
    }
}



SearchableWidget.propTypes = {
    dataURL: PropTypes.string.isRequired,
    displayField: PropTypes.string.isRequired,
    onSelect: PropTypes.func.isRequired,
    onClear: PropTypes.func.isRequired,
    idField: PropTypes.string.isRequired

}

export default SearchableWidget;