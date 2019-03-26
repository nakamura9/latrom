import React, {Component} from 'react';
import  ExpenseEntry from './entries/expense'
import  ServiceEntry from './entries/service'
import  ProductEntry from './entries/product'
import axios from 'axios';


class EntryWidget extends Component{
    state ={
        focused: "product",
        billables: [],
        inputs: {
            }
    }

    componentDidMount =() =>{
        let customer = document.getElementById('id_customer');
        customer.addEventListener('change', (evt) =>{
            axios({
                method: 'get',
                url: '/invoicing/api/customer/' + evt.target.value
            }).then(res =>{
                this.setState({billables: res.data.expense_set})
            })
        })
    }
    clickHandler = (evt) =>{
        this.setState({'focused': evt.target.id})
    }

    //sale methods 
    handleProductSelect = (data) =>{
        this.setState({inputs: data});
    }
    handleProductClear = () =>{
        this.setState({inputs: {}});
    }

    handleProductQuantity = (evt) =>{
        let newInputs = {...this.state.inputs};
        newInputs['quantity'] = evt.target.value;
        this.setState({inputs: newInputs});
    }

    //service methods 

    handleServiceSelect = (data) =>{
        this.setState({inputs: data});
    }
    handleServiceClear = () =>{
        this.setState({inputs: {}});
    }

    handleServiceHours = (evt) =>{
        let newInputs = {...this.state.inputs};
        newInputs['hours'] = evt.target.value;
        this.setState({inputs: newInputs});
    }

    //billables
    handleBillable = (value) =>{
        const pk = value.split('-')[0];
        axios({
            method: 'get',
            url: '/accounting/api/expense/' + pk 
        }).then(res =>{
            this.setState({inputs: {
                selected: value,
                amount: res.data.amount,
                description: res.data.description
            }})
        })
    }

    insertHandler = () =>{
        const data = {
            type: this.state.focused,
            ...this.state.inputs
        }
        this.props.insertHandler(data)
    }

    render(){
        const tabStyle = {
            listStyleType: 'none',
            display: 'inline-block',
            borderRadius: '5px 5px 0px 0px',
            padding: '5px 10px',
            borderStyle: 'solid',
            borderColor: 'white'

        }

        const windowStyle = {
            width: '100%',
            padding: '10px',
            border: '0px 1px 1px 1px solid white',
        }
        return(
            <div style={{
                color: 'white',
                backgroundColor: '#007bff',
                padding: '10px'
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
                <div>
                    <div style={{...windowStyle,
                        'display': this.state.focused === "product"
                            ?'block' 
                            :'none'
                        }}><ProductEntry
                                    itemList={this.props.itemList} 
                                    onSelect={this.handleProductSelect}
                                    onClear={this.handleProductClear}
                                    onChangeQuantity={this.handleProductQuantity}
                                    /></div>
                    <div style={{...windowStyle,
                        'display': this.state.focused === "service"
                            ?'block' 
                            :'none'
                        }}><ServiceEntry 
                                    itemList={this.props.itemList}
                                    onSelect={this.handleServiceSelect}
                                    onClear={this.handleServiceClear}
                                    onChangeHours={this.handleServiceHours} /></div>
                    <div style={{...windowStyle,
                        'display': this.state.focused === "expense"
                            ?'block' 
                            :'none'
                        }}><ExpenseEntry
                                itemList={this.props.itemList} 
                                billables={this.state.billables}
                                handler={this.handleBillable}/></div>
                </div>
                <button onClick={this.insertHandler} className="btn" style={{float:'right'}}>Insert</button>
            </div>
        )
    }
}


export default EntryWidget;