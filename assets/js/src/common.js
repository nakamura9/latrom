import React, {Component} from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';

const DeleteButton = (props) => {
        return(
            <button
                className="btn btn-danger"
                type="button"
                onClick={() => (props.handler(props.index))}>
                <i className="fas fa-trash"></i>
            </button>
        );
    }

DeleteButton.propTypes = {
    handler: PropTypes.func.isRequired,
    index: PropTypes.number.isRequired
}

class Totals extends Component{
    state = {
        taxObj: null,
        tax: 0.00,
        subtotal: 0.00,
        total: 0.00
    }
    componentDidMount(){
        //get sales tax
        axios({
            method: "GET",
            url: "/invoicing/api/config/1"
        }).then(res =>{
            console.log(res);
            this.setState({taxObj: res.data.sales_tax})
        })
    }
    componentDidUpdate(prevProps, prevState){
        if(prevProps.list !== this.props.list){
            //update totals 
            let subtotal = this.props.list.reduce(this.props.subtotalReducer, 0);
            console.log(subtotal);
            let taxAmount;
            if(this.state.taxObj){
                taxAmount = subtotal * (this.state.taxObj.rate / 100);
            }else{
                taxAmount = 0.0;
            }
            let total = subtotal + taxAmount;
            this.setState({
                subtotal : subtotal,
                tax : taxAmount,
                total : total
            });
        }
    }
    render(){
        let contents;
        if(this.state.tax === null){
            contents = (
                <tfoot>
                    <tr>
                        <th colSpan={this.props.span - 1}>Total</th>
                        <td>{this.state.total}</td>
                    </tr>
                </tfoot>
            )
        }else{
            contents = (
                <tfoot>    
                    <tr>
                            <th colSpan={this.props.span - 1}>Subtotal</th>
                            <td>{this.state.subtotal.toFixed(2)}</td>
                        </tr>
                        <tr>
                            <th colSpan={this.props.span - 1}>Tax</th>
                            <td>{this.state.tax.toFixed(2)}</td>
                        </tr>
                        <tr>
                            <th colSpan={this.props.span - 1}>Total</th>
                            <td>{this.state.total.toFixed(2)}</td>
                        </tr>
                </tfoot>
                )
        }
        return(contents);
    }
}

Totals.propTypes = {
    span: PropTypes.number.isRequired,
    list: PropTypes.array.isRequired,
    subtotalReducer: PropTypes.func.isRequired
}

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

export {DeleteButton, Totals, SearchableWidget};