import React, {Component} from 'react';
import axios from 'axios';

class InventorySelectWidget extends Component {
    //currValue is whats being typed, selected is the value validated
    state = {
        items: [],
        choices: [],
        currValue: "",
        selectedValue: ""
    }

    componentDidUpdate(prevProps, prevState){
        if (this.props.list.length !== prevProps.list.length){
            this.setState({
                currValue : "",
                selectedValue: ""
            }) 
        }
    }

    componentDidMount(){
        axios({
            method: "GET",
            url: '/inventory/api/product'
        }).then(res => {
            let newChoices = res.data.map((item) =>{
                return('P' + item['id'] + " - " + item['name'])
            });

            this.setState({
                items: res.data,
                choices: newChoices
            }, () => {
                    axios({
                        method: "GET",
                        url: '/inventory/api/equipment'
                    }).then(res => {
                        let additionalChoices = res.data.map((item) =>{
                            return('E' + item['id'] + " - " + item['name'])
                        });
                        let newItems = this.state.items.concat(res.data);
                        let newChoices = this.state.choices.concat(additionalChoices);
                        this.setState({
                            items: newItems,
                            choices: newChoices
                        }, () => {
                            axios({
                                method: "GET",
                                url: '/inventory/api/consumable'
                            }).then(res => {
                                let additionalChoices = res.data.map((item) =>{
                                    return('C' + item['id'] + " - " + item['name'])
                                });
                                let newItems =this.state.items.concat(res.data);
                                let newChoices = this.state.choices.concat(
                                    additionalChoices);
                                this.setState({
                                    items: newItems,
                                    choices: newChoices
                                });
                            })
                        });
                });
            });
        });
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
                <div style={{width:'100%'}}>
                    <span>{this.state.selectedValue}</span>
                    <span style={{float:'right'}}>
                        <button 
                            className="btn btn-secondary"
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
                    {this.state.choices.map((choice, i) => {
                        //always display id and display field
                        return(<option key={i} >
                                {choice}
                            </option>)
                    })}
                    
                </datalist>
            </div>
        );
    }
}

export default InventorySelectWidget;