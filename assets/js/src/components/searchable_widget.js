import React, {Component} from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import OptionsWidget from "./options_widget";
import Radium from 'radium';

// TODO make sure that on clear works, replace caret with times when deleting 
//data
//For prepopulated searchable widgets, we provide a prepoulating url, including 
//any params it requires.
//we then provided a prepopulationHandler that takes the async response and 
//returns the appropriate value to be set to the selected state value

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
        }
        if(this.props.resetFlag && this.props.resetFlag != prevProps.resetFlag){
            this.setState({
                currValue: "",
                selectedValue: ""
            })
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
            }, () =>{
                if(this.props.prePopulatedURL){
                    axios.get(this.props.prePopulatedURL).then(res => {
                        const selected = this.props.prePopulationHandler(
                            res.data);
                        this.props.onSelect(selected);
                        this.setState({
                            selectedValue:  selected,
                            currValue: selected
                        })
                    })
                }
            });
            
        })
    }

    updateChoices = () =>{
        // retrieves the latest object from the database
        if(!this.props.model){
            return
        }
        axios({
            'method': 'GET',
            url: '/base/models/get-latest/' + this.props.app+ '/' + this.props.model
        }).then((resp) =>{
            if(!(resp.data.data === -1)){
                const pk = resp.data.data[0];
                const itemString = resp.data.data[1];
                let label;
                if(itemString.indexOf('-') === -1){
                    label=itemString;
                }else{
                    label = itemString.split('-')[1]
                }
                let isPresent = false;
                this.state.choices.forEach((i) =>{
                    const [id, name] = i.split('-');
                    if(id == pk){
                        isPresent = true;
                    }
                });

                if(!isPresent){
                    let newChoices = this.state.choices;
                    newChoices.push(pk.toString() + ' - ' + label);
                    this.setState({choices: newChoices});
                }
            }
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
        
        this.updateChoices()
        if(this.state.selectedValue){
            this.clearValue()
        }else{
            this.setState((prevState) =>({
                optionsHidden: !prevState.optionsHidden
            }))
        }
        
    }

    showOptions = () =>{
        this.updateChoices();
        this.setState({optionsHidden: false});
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
            val.toLowerCase().indexOf(evt.target.value.toLowerCase()) !== -1
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
            <div id={this.props.widgetID} style={this.props.widgetID ? {} :{
                width:"100%",
                margin: "2px",
                position:"relative",
                display: "inline-block"
                }}>
                <TextBoxWidget 
                    idRoot={this.props.widgetID}
                    currValue={this.state.currValue}
                    validChoice={this.state.selectedValue}
                    handleChange={this.handleChange}
                    toggleOptions={this.toggleOptions}
                    showOptions={this.showOptions}
                    hideOptions={this.hideOptions}
                    bordered={this.props.bordered}/>
                   
                <OptionsWidget 
                    closeDropdown={() => this.setState({optionsHidden: true})}
                    choices={this.state.filteredChoices}
                    onSelectValue={this.onSelectValue}
                    hidden={this.state.optionsHidden}
                    newLink={this.props.newLink}/>
            </div>
        );
    }
}


class TextBoxWidget extends Component{
    componentDidMount(){
        let input = document.getElementById(`${this.props.idRoot}-input`);
        input.addEventListener('focus', () =>{
            this.props.showOptions();
        })
    }

    render(){
        let icon;
        if(this.props.validChoice === ""){
            icon = "fa-angle-down"
        }else{
            icon = "fa-times"
        }
        return(<div 
                id={this.props.idRoot ?  `${this.props.idRoot}-text-box` : '' } 
                style={this.props.idRoot ? {} :{
            padding: "3px", 
            backgroundColor: "white", 
            borderRadius: "2px"}}>
        <input 
            id={`${this.props.idRoot}-input`}
            type="text"
            value={this.props.currValue}
            onChange={this.props.handleChange}
            placeholder="Select item..."
            style={{
                padding: "3px",
                border: this.props.bordered ? "1px" : "0px",
                width:"85%",
                backgroundColor: this.props.validChoice === "" ?
                    "#fff" : "#b0e0e6"
        }}/>
        <button type="button" style={{
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

export default Radium(SearchableWidget);