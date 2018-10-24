import React, {Component} from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';


class SearchableWidget extends Component {
    //currValue is whats being typed, selected is the value validated
    state = {
        items: [],
        choices: [],
        currValue: "",
        selectedValue: ""
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
                items: res.data,
                choices: newChoices
            });
        })
    }

    handleChange = (evt) => {
        let selectedValue = "";
        let index = this.state.choices.indexOf(evt.target.value);
        
        if(index !== -1){
            selectedValue = evt.target.value;

        }
        this.setState({
            currValue: evt.target.value,
            selectedValue: selectedValue
        });
        if(index !== -1){
            this.props.onSelect(evt.target.value);
        }
    }
    render(){
        let rendered;
        if(this.state.selectedValue === ""){
            rendered = (
                <input 
                    type="text"
                    className="form-control"
                    value={this.state.currValue}
                    onChange={this.handleChange}
                    placeholder="Select item..."
                    list="id_list"/>
            )
        }else{
            rendered = (
                <div style={{
                    width:'100%', 
                    margin: '0px', 
                    minHeight: '35px',
                    backgroundColor: '#ccc'
                }} >
                    <span>{this.state.selectedValue}</span>
                    <span style={{float:'right'}}>
                        <button 
                            style={{
                                backgroundColor: '#',
                                color: 'white',
                                border: '0px',
                                boxShadow: 'none',
                                minHeight: '35px',
                                minWidth: '35px'
                            }}
                            onClick={() =>{
                                this.setState({
                                    selectedValue: "",
                                    currValue: ""
                                });
                                this.props.onClear();
                            }}>
                            <i className="fas fa-times"></i>
                        </button>
                    </span>
                </div>
            )
        }
        return(
            <div>
                {rendered}   
                <datalist id="id_list">
                    {this.state.items.map((item, i) => {
                        //always display id and display field
                        return(<option key={i} >
                                {item[this.props.idField]} - {item[this.props.displayField]}
                            </option>)
                    })}
                    
                </datalist>
            </div>
        );
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