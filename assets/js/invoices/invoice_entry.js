import React, {Component} from 'react';
import  ExpenseEntry from './entries/expense'
import  ServiceEntry from './entries/service'
import  ProductEntry from './entries/product'
import axios from 'axios';


class EntryWidget extends Component{
    state ={
        focused: "product",
        billables: [],
        inputs: {},
        
    }

    componentDidMount =() =>{
        let customer = document.getElementById('id_customer');
        //initial value
        this.setBillables(customer.value);
        //event handler
        $("#id_customer").on('change', (evt) =>{
            this.setBillables(evt.target.value)
        })
    }

    setBillables = (customer) =>{
        axios({
            method: 'get',
            url: '/invoicing/api/customer/' + customer
        }).then(res =>{
            this.setState({billables: res.data.expense_set})
        })
    }

    clickHandler = (evt) =>{
        this.setState({'focused': evt.target.id})
    }
    entryChangeHandler = (data) =>{
        //duplicates the state of the child elements
        this.setState({inputs: data})
    }


    insertHandler = () =>{
        if(!this.state.inputs.tax){
            alert('tax is required')
        }else if(!this.state.inputs.selected){
            alert('a valid choice must be selected')
        }else{
            const data = {
                type: this.state.focused,
                ...this.state.inputs
            }
            this.props.insertHandler(data)
            this.setState({inputs: {}})
        }
        
    }

    render(){
        const tabStyle = {
            listStyleType: 'none',
            display: 'inline-block',
            borderRadius: '5px 5px 0px 0px',
            padding: '5px',
            borderStyle: 'solid',
            borderColor: 'white'

        }

        const windowStyle = {
            width: '100%',
            padding: '5px',
            border: '0px 1px 1px 1px solid white',
        }
        return(
            <div style={{
                color: 'white',
                backgroundColor: '#007bff',
                padding: '5px'
            }}>
                <ul style={{listStylePosition: 'inside', paddingLeft: '0px'}}>
                    <li 
                        id="product" 
                        style={{...tabStyle,
                            borderWidth: this.state.focused ==="product"
                            ? '1px 1px 0px 1px '
                            : '0px 0px 1px 0px ',}}
                        onClick={this.clickHandler}>Product</li>
                    <li 
                        id="service" 
                        style={{...tabStyle,
                            borderWidth: this.state.focused ==="service"
                            ? '1px 1px 0px 1px '
                            : '0px 0px 1px 0px ',}}
                        onClick={this.clickHandler}>Service</li>
                    <li 
                        id="expense" 
                        style={{...tabStyle,
                            borderWidth: this.state.focused ==="expense"
                            ? '1px 1px 0px 1px '
                            : '0px 0px 1px 0px ',}}
                        onClick={this.clickHandler}>Expense</li>
                </ul>
                <div className="entry-style">
                    <div style={{...windowStyle,
                        'display': this.state.focused === "product"
                            ?'block' 
                            :'none'
                        }}><ProductEntry
                                itemList={this.props.itemList} 
                                changeHandler={this.entryChangeHandler}     insertHandler={this.insertHandler}/></div>
                    <div style={{...windowStyle,
                        'display': this.state.focused === "service"
                            ?'block' 
                            :'none'
                        }}><ServiceEntry 
                                itemList={this.props.itemList}
                                changeHandler={this.entryChangeHandler}
                                insertHandler={this.insertHandler}/>
                                    </div>
                    <div style={{...windowStyle,
                        'display': this.state.focused === "expense"
                            ?'block' 
                            :'none'
                        }}><ExpenseEntry
                                itemList={this.props.itemList} 
                                billables={this.state.billables}
                                changeHandler={this.entryChangeHandler}
                                insertHandler={this.insertHandler}/></div>
                                </div>
                
            </div>
        )
    }
}


export default EntryWidget;