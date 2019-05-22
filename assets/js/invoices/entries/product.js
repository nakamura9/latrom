import React, {Component} from 'react';
import SearchableWidget from '../../src/components/searchable_widget';
import AsyncSelect from '../../src/components/async_select';
import axios from 'axios';

class ProductEntry extends Component{
    state = {
        quantity: 0,
        unitPrice: 0,
        discount: 0,
        tax: 0,
        selected: ""
    }

    componentDidUpdate(prevProps, prevState){
        if (this.props.itemList.length !== prevProps.itemList.length){
            this.setState({
                quantity: 0,
                unitPrice: 0,
                discount: 0,
                tax: 1,
            })
            let tax = document.getElementById('product-tax');
            tax.value = 1;
        }
    }

    handler = (evt) =>{
        const name = evt.target.name;
        let newState = {...this.state};
        newState[name] = evt.target.value
        this.setState(newState, () => this.props.changeHandler(this.state));
    }

    handleProductSelect = (value) =>{
        const pk = value.split('-')[0];
        axios({
            'method': 'get',
            'url': '/inventory/api/inventory-item/' + pk 
        }).then((res)=>{
            //tax 
            let tax = document.getElementById('product-tax');
            if(res.data.product_component.tax){
                tax.value = res.data.product_component.tax.id;
            }

            this.setState({
                unitPrice: res.data.unit_sales_price,
                tax:res.data.product_component.tax.id + ' - ' + 
                        res.data.product_component.tax.name + '@' +
                        res.data.product_component.tax.rate,
                selected: value
            }, 
                () => this.props.changeHandler(this.state))
        })
        
    }

    handleProductClear = () =>{
        let tax = document.getElementById('product-tax');
        tax.value = 1;
        this.setState({
            quantity: 0,
            unitPrice: 0,
            selected: '',
            discount: 0
        }, () => this.props.changeHandler(this.state));
    }

    taxHandler = (value) =>{
        axios({
            method: 'get',
            url: '/accounting/api/tax/' + value
        }).then(res =>{
            this.setState({tax: res.data.id + ' - ' 
                                + res.data.name  + '@' 
                                + res.data.rate}, 
                () => this.props.changeHandler(this.state))

        })
    }
    
    render(){
        return(
            <div>
                <table style={{width:"100%"}}>
                    <thead>
                        <tr>
                            <th style={{width: '35%'}}>Product</th>
                            <th style={{width: '10%'}}>Unit Price</th>
                            <th style={{width: '10%'}}>Quantity</th>
                            <th style={{width: '15%'}}>Discount</th>
                            <th style={{width: '15%'}}>Tax</th>
                            <td style={{width: '15%'}}></td>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td >
                                <SearchableWidget
                                    widgetID="product-widget"
                                    list={this.props.itemList}
                                    dataURL="/inventory/api/product/"
                                    displayField="name"
                                    idField="id"
                                    model="inventoryitem"
                                    app="inventory"
                                    canCreateNewItem={true}
                                    newLink='/inventory/product-create/'
                                    onSelect={this.handleProductSelect}
                                    onClear={this.handleProductClear} />
                            </td>
                            <td >
                                <input 
                                    type="number"
                                    name="unitPrice"
                                    onChange={this.handler}
                                    value={this.state.unitPrice}
                                     />
                            </td>
                            <td >
                                <input 
                                    type="number"
                                    name="quantity"
                                    value={this.state.quantity}
                                    onChange={this.handler}/>
                            </td>
                            <td >
                                <input 
                                    type="number"
                                    name="discount"
                                    value={this.state.discount}
                                    
                                    onChange={this.handler}/>
                            </td>
                            
                            <td >
                                {/*Use a tax choice field */}
                                <AsyncSelect 
                                    noCSS
                                    ID='product-tax'
                                    dataURL="/accounting/api/tax"
                                    name="tax"
                                    resProcessor={(res) =>{
                                        return res.data.map((tax) =>({
                                            name: tax.name,
                                            value: tax.id
                                        }))
                                    }}
                                    handler={this.taxHandler}/>
                            </td>
                            <td>
                                <button 
                                    onClick={this.props.insertHandler} 
                                    className="invoice-btn" >Insert</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            )   
    }
}

export default ProductEntry;