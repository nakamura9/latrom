import React, {Component} from 'react';
import SearchableWidget from '../../src/components/searchable_widget';
import axios from 'axios';

class ProductEntry extends Component{
    state = {
        quantity: 0,
        unitPrice: 0,
        selected: ""
    }

    componentDidUpdate(prevProps, prevState){
        if (this.props.itemList.length !== prevProps.itemList.length){
            this.setState({
                quantity: 0,
                unitPrice: 0
            })
            //remove selected choice from list of choices 
        }
    }

    handler = (evt) =>{
        const name = evt.target.name;
        let newState = {...this.state};
        newState[name] = evt.target.value
        this.setState(newState);
        this.props.onChangeQuantity(evt);
    }

    handleProductSelect = (value) =>{
        const pk = value.split('-')[0];
        axios({
            'method': 'get',
            'url': '/inventory/api/inventory-item/' + pk 
        }).then((res)=>{
            this.setState({
                unitPrice: res.data.unit_sales_price,
                selected: value
            }, 
                () => this.props.onSelect(this.state))
        })
        
    }

    handleProductClear = () =>{
        this.setState({
            quantity: 0,
            unitPrice: 0,
            selected: ''
        })
        this.props.onClear();
    }

    render(){
        return(
            <div>
                <table style={{width:"100%"}}>
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>Unit Price</th>
                            <th>Quantity</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style={{width: '60%'}}>
                                <SearchableWidget
                                    list={this.props.itemList}
                                    dataURL="/inventory/api/product/"
                                    displayField="name"
                                    idField="id"
                                    canCreateNewItem={true}
                                    newLink='/inventory/product-create/'
                                    onSelect={this.handleProductSelect}
                                    onClear={this.handleProductClear} />
                            </td>
                            <td>
                                <input 
                                    type="number"
                                    name="unitPrice"
                                    value={this.state.unitPrice}
                                    className="form-control" />
                            </td>
                            <td>
                                <input 
                                    type="number"
                                    name="quantity"
                                    value={this.state.quantity}
                                    className="form-control"
                                    onChange={this.handler}/>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            )   
    }
}

export default ProductEntry;